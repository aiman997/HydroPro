import os
import asyncio
import asyncpg
import logging
import redis.asyncio as redis
from lib.service import Service
from aioprometheus import Gauge
from aioprometheus.pusher import Pusher
import bcrypt

DB			     = os.environ.get('DB')
PREFIX            = "HYDRO::USER::"
PUSH_GATEWAY_ADDR = os.environ.get('PUSH_GATEWAY_ADDR')
PUSH_GATEWAY_ADDR = "http://prometheus-push-gateway:9091"
POSTGRES_NAME     = os.environ.get('POSTGRES_DB')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

logging.basicConfig(level=logging.DEBUG)

class Users(Service):
	def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider):
		Service.__init__(self, name, stream, streams, actions, redis_conn, metrics_provider)
		self.newusers_metric = Gauge("newusers", "Users registered")



	async def handel_event(self, event):
		
		logging.info(event)

		try:
			conn = await asyncpg.connect(dsn="postgres://postgres:NxVhhyU9p3@postgres:5432/hydrodb")
			# conn = await asyncpg.connect(user='postgres', password="NxVhhyU9p3", host='postgres', port='5432', database="hydrodb")
			if 'newuser' in event.keys():
				email = event['newuser']['email']  
				password = event['newuser']['password']
				rpi_address = event['newuser']['rpi_address']
				first_name = event['newuser']['first_name']
				last_name = event['newuser']['last_name']
				plant_id = event['newuser']['plant_id']
				active = event['newuser']['active']
				roles = event['newuser']['roles']
				hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
				new_user_id = await conn.fetchval(f"INSERT INTO users.user(plant_id, email, password, first_name, last_name, active, roles) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id", plant_id, email, str(hashed_password), first_name, last_name, active, roles)
				await conn.close()
				logging.info(f"New user inserted with ID: {new_user_id}")
					

			elif 'authuser' in event.keys():
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

		except Exception as e:
			logging.error(f"Error: {e}")

		await self.send_event('newuser', event)

	async def add_new_user(self, user: dict):
		if not self.conn:
			try:
				self.conn = await asyncpg.connect(user='postgres', password=POSTGRES_PASSWORD, host='postgres', port='5432', database="hydrodb")
				hashed_password = bcrypt.hashpw(user['password'].encode(), bcrypt.gensalt())
				user['password'] = hashed_password.decode()
				await self.conn.execute('''INSERT INTO hydro.users (email, rpi_address, password)
													 VALUES ($1, $2, $3)''', user['email'], user['rpi_address'], user['password'])
			except Exception as e:
				logging.error(f" from con {e}")

	async def close_conn(self):
		if self.conn:
			await self.conn.close()
			self.conn = None

async def main():
	svc = Users('users', 'users', ['api'], ['newuser', 'authuser', 'resetuser', 'deluser'], redis.Redis(host='redis', port=6379, decode_responses=False), Pusher("metric", PUSH_GATEWAY_ADDR, grouping_key={"instance": 'metric'}))
	loop.create_task(svc.listen())

if __name__ == '__main__':
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	logging.info(f"Starting...")
	loop.run_until_complete(main())
	loop.run_forever()


