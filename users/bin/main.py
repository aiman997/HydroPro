import os
import asyncio
import asyncpg
import logging
import redis.asyncio as redis
from lib.service import Service
from aioprometheus import Gauge
from aioprometheus.pusher import Pusher
import bcrypt

DB			     = 'postgresql://postgres:NxVhhyU9p3@postgres/hydrodb' # os.environ.get('DB')
PREFIX            = "HYDRO::USER::"
PUSH_GATEWAY_ADDR = os.environ.get('PUSH_GATEWAY_ADDR')
PUSH_GATEWAY_ADDR = "http://prometheus-push-gateway:9091"

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
				rpi_address = event['rpi_address']
				first_name = event['first_name']
				last_name = event['last_name']
				plant_id = event['plant_id']
				active = event['active']
				roles = event['roles']
				hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
				new_user_id = await conn.fetchval(f"INSERT INTO users.user(plant_id, email, password, first_name, last_name, active, roles) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id", plant_id, email, str(hashed_password), first_name, last_name, active, roles)
				await conn.close()
				return {"success": 1, "user_id": new_user_id}
			except Exception as e:
				logging.error(f"Error while newuser: {e}")
				return {"error": e}


		async def handel_event(self, event):
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

			await self.send_event('newuser', event)

async def main():
	svc = Users('users', 'users', ['api'], ['newuser', 'authuser', 'resetuser', 'deluser'], redis.Redis(host='redis', port=6379, decode_responses=False), Pusher("metric", PUSH_GATEWAY_ADDR, grouping_key={"instance": 'metric'}))
	loop.create_task(svc.listen())

if __name__ == '__main__':
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	logging.info(f"Starting...")
	loop.run_until_complete(main())
	loop.run_forever()
