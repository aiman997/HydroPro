import asyncio
import logging
import os

import asyncpg
import bcrypt
import redis.asyncio as redis
from aioprometheus import Gauge
from aioprometheus.pusher import Pusher
from lib.service import Service

DB			     = 'postgresql://postgres:NxVhhyU9p3@postgres/hydrodb' # os.environ.get('DB')
PREFIX            = "HYDRO::AUTH::"
PUSH_GATEWAY_ADDR = os.environ.get('PUSH_GATEWAY_ADDR')

logging.basicConfig(level=logging.DEBUG)

class Auth(Service):
		def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider):
			Service.__init__(self, name, stream, streams, actions, redis_conn, metrics_provider)
			self.authusers_metric = Gauge("authusers", "Users authenticated")
			self.rpcs.append('authuser')

		@Service.rpc
		async def authuser(self, event):
			logging.info(event)
			try:
				conn = await asyncpg.connect(dsn=DB)
				await conn.close()
				email = event['email']
				password = event['password']
				hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
				await self.send_event('authenticated', {"email": email, "untill": '', "token": '', "refresh_token": ''})
			except Exception as e:
				logging.error(f"Error while authuser: {e}")
				return {"error": e}


		async def handel_event(self, event):
			logging.info(event)

			try:
				if 'authuser' in event.keys():
					logging.info(f"resetuser event: password for {event} reset")

				elif 'deluser' in event.keys():
					email = event['deluser']['email']
					logging.info(f"deluser event: {email} deleted from the database")
					await self.send_event('unauthenticated', event)
				else:
					logging.error(f"Error: Invalid event")

			except Exception as e:
				logging.error(f"Error: {e}")

async def main():
	svc = Auth('auth', 'auth', ['api', 'users'], ['newuser', 'authuser', 'resetuser', 'deluser'], redis.Redis(host='redis', port=6379, decode_responses=False), Pusher("metric", PUSH_GATEWAY_ADDR, grouping_key={"instance": 'auth'}))
	loop.create_task(svc.listen())

if __name__ == '__main__':
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	logging.info(f"Starting...")
	loop.run_until_complete(main())
	loop.run_forever()
