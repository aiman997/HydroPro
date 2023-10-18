import asyncio
import logging
import os

import asyncpg
import bcrypt
import redis.asyncio as redis
from aioprometheus import Gauge
from aioprometheus.pusher import Pusher
from lib.service import Service

DB = os.environ.get('DB')
PREFIX = "HYDRO::USER::"
PUSH_GATEWAY_ADDR = os.environ.get('PUSH_GATEWAY_ADDR')

logging.basicConfig(level=logging.DEBUG)

class Users(Service):
		def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider):
			Service.__init__(self, name, stream, streams, actions, redis_conn, metrics_provider)
			self.newusers_metric = Gauge("newusers", "Users registered")
			self.rpcs.append('newuser')

		@Service.rpc
		async def newuser(self, event):
			logging.info(event)
			try:
				conn = await asyncpg.connect(dsn=DB)
				email = event['email']
				password = event['password']
				first_name = event['first_name']
				last_name = event['last_name']
				active = 0
				roles = event['roles']
				hashed_password = bcrypt.hashpw(password.encode('utf-8'), self.salt).decode('utf-8')
				new_user_id = await conn.fetchval(f"SELECT * FROM users.insert_user($1::TEXT, $2::TEXT, $3::TEXT, $4::TEXT, $5::BOOLEAN, $6::VARCHAR);", email, str(hashed_password), first_name, last_name, active, roles)
				await conn.close()
				self.newusers_metric.inc({"type": "new_user"})
				await self.send_event('authuser', event)
				return {"success": 1, "user_id": new_user_id}
			except Exception as e:
				logging.error(f"Error while newuser: {e}")
				return {"error": 1, "message": f"Exception occuried: {e}"}


		async def handle_event(self, event):
			logging.info(event)

			try:
				conn = await asyncpg.connect(dsn=DB)
				if 'authuser' in event.keys():
					email = event['authuser']['email']
					password = event['authuser']['password']
					result = await conn.fetchrow("SELECT * FROM users.user WHERE email = $1", email)
					if bcrypt.checkpw(password.encode(), result['password'].encode()):
						logging.info(f"authuser event: {email} authenticated")
					else:
						logging.info(f"authuser event: {email} not authenticated")

				elif 'resetuser' in event.keys():
					email = event['resetuser']['email']
					new_password = event['resetuser']['new_password']
					hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
					await conn.execute("UPDATE users.user SET password = $1 WHERE email = $2", hashed_password.decode(), email)
					logging.info(f"resetuser event: password for {email} reset")

				elif 'deluser' in event.keys():
					email = event['deluser']['email']
					await conn.execute("DELETE FROM users.user WHERE email = $1", email)
					logging.info(f"deluser event: {email} deleted from the database")
				else:
					logging.error(f"Error: Invalid event")

				await conn.close()
			except Exception as e:
				logging.error(f"Error: {e}")

			await self.send_event('_newuser', event)

async def main():
	svc = Users('users', 'users', ['api'], ['newuser', 'authuser', 'resetuser', 'deluser'], redis.Redis(host='redis', port=6379, decode_responses=False), Pusher("metric", PUSH_GATEWAY_ADDR, grouping_key={"instance": 'users'}))
	loop.create_task(svc.listen())

if __name__ == '__main__':
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	logging.info(f"Starting...")
	loop.run_until_complete(main())
	loop.run_forever()
