import asyncio
import logging
import os
import asyncpg
import redis.asyncio as redis
from aioprometheus import Gauge
from aioprometheus.pusher import Pusher
from lib.service import Service

DB			     = 'postgresql://postgres:NxVhhyU9p3@postgres/hydrodb' # os.environ.get('DB')
PREFIX            = "HYDRO::AUTH::"
PUSH_GATEWAY_ADDR = os.environ.get('PUSH_GATEWAY_ADDR')

logging.basicConfig(level=logging.DEBUG)

class Plant(Service):
		def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider):
			Service.__init__(self, name, stream, streams, actions, redis_conn, metrics_provider)
			self.plant_metric = Gauge("createplant", "New plant added")
			self.rpcs.append('newplant')

		@Service.rpc
		async def newplant(self, event):
			logging.info(event)
			try:
				conn = await asyncpg.connect(dsn=DB)
				rpi_id = event['rpi_id']
				plant_name = event['plant_name']
				result = await conn.fetchrow("CALL plants.insert_plant( $1::INT, $2 )", int(rpi_id), plant_name)
				await conn.close()
				await self.send_event('plantcreated', {'result': result})
				return {"success": 1, "message": result}
			except Exception as e:
				logging.error(f"Error while authuser: {e}")
				return {"error": e}


		async def handel_event(self, event):
			logging.info(event)


async def main():
	svc = Plant('plant', 'plant', ['api'], ['newplant'], redis.Redis(host='redis', port=6379, decode_responses=False), Pusher("metric", PUSH_GATEWAY_ADDR, grouping_key={"instance": 'plant'}))
	loop.create_task(svc.listen())

if __name__ == '__main__':
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	logging.info(f"Starting...")
	loop.run_until_complete(main())
	loop.run_forever()
