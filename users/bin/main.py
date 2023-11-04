import asyncio
import logging
import os

import asyncpg
import bcrypt
import redis.asyncio as redis
from aioprometheus import Gauge
from aioprometheus.pusher import Pusher
from lib.service import Service

DB = os.environ.get("DB")
PREFIX = "HYDRO::USER::"
PUSH_GATEWAY_ADDR = os.environ.get("PUSH_GATEWAY_ADDR")

logging.basicConfig(level=logging.DEBUG)


class Users(Service):
    def __init__(self, name, streams, actions, redis_conn, metrics_provider):
        Service.__init__(self, name, streams, actions,
                         redis_conn, metrics_provider)
        self.salt = bcrypt.gensalt()
        self.newusers_metric = Gauge("newusers", "Users registered")
        self.rpcs.append("newuser")

    @Service.rpc
    async def newuser(self, event):
        logging.info(event)
        try:
            conn = await asyncpg.connect(dsn=DB)
            username = event["username"]
            email = event["email"]
            first_name = event["first_name"]
            last_name = event["last_name"]
            roles = event["roles"]
            password = event["password"]
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), self.salt).decode(
                "utf-8"
            )
            new_user = await conn.fetchrow(
                f"""
                SELECT *
                  FROM users.create_user(
                        $1::VARCHAR(255),
                        $2::VARCHAR(255),
                        $3::VARCHAR(100),
                        $4::VARCHAR(100),
                        $5::VARCHAR(50),
                        $6::TEXT
                       );
                """,
                username,
                email,
                first_name,
                last_name,
                roles,
                str(hashed_password),
            )
            await conn.close()
            self.newusers_metric.inc({"type": "new_user"})
            await self.send_event("authuser", event)
            return {"success": 1, "user": new_user}
        except Exception as e:
            logging.error(f"Error while newuser: {e}")
            return {"error": 1, "message": f"Exception occuried: {e}"}

    async def handle_event(self, event):
        logging.info(event)

async def main():
    svc = Users(
        "users",
        ["api"],
        ["newuser", "authuser", "resetuser", "deluser"],
        redis.Redis(host="redis", port=6379, decode_responses=False),
        Pusher("metric", PUSH_GATEWAY_ADDR,
               grouping_key={"instance": "users"}),
    )
    loop.create_task(svc.listen())


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logging.info(f"Starting...")
    loop.run_until_complete(main())
    loop.run_forever()
