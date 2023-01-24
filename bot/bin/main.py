import os
import json
import asyncio
import logging
import redis.asyncio as redis
from lib.service import Service
from aioprometheus.pusher import Pusher

PREFIX = "HYDRO::PLANT"
PUSH_GATEWAY_ADDR = "http://prometheus-push-gateway:9091"

logging.basicConfig(level=logging.INFO)

class Hydro(Service):
		def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider, params):
			Service.__init__(self, name, stream, streams, actions, redis_conn, metrics_provider)
			self.params = params

		async def handel_event(self, event):
			logging.debug(f"Handling event: {event}")
			try:
				await self.adjust(event)
			except Exception as e:
				logging.error(f"Error: {e}")
			logging.debug(f"Event handled successfully")

		async def execute_cmd(self, command, **kwargs):
			await self.send_event('update', {'command': command})

		async def adjust(self, args, **kwargs):
			logging.info(f"Sending message to rpi {args}: {kwargs}")
			if float(args["ec"]) < float(self.params["EC_MIN"]):
				logging.info("Turning on ECUP pump for 3 seconds")
				await self.execute_cmd("pec")
				logging.info("Turning on MAIN pump for 5 minutes / 40 Liters")
				await self.execute_cmd("mp")
				logging.info("Turning off MAIN pump for 5 minutes  / until waterlevel sensor detects water")
				await self.execute_cmd("mp")

			if float(args["ec"]) > float(self.params["EC_MAX"]):
				logging.info("Turning on Solenoid Valve Out for 2 minutes / 10 Liters")
				await self.execute_cmd("svo")
				logging.info("Turning off Solenoid Valve OUT")
				await self.execute_cmd("svo")
				logging.info("Turning on Solenoid Valve In for 2 minutes / 10 Liters / Until waterlevel sensor detects water")
				await self.execute_cmd("svi")
				logging.info("Turning on MAIN pump for 5 minutes / 40 Liters")
				await self.execute_cmd("mp")
				logging.info("Turning off MAIN pump for 5 minutes  / until waterlevel sensor detects water")
				await self.execute_cmd("mp")

			if float(args["ph"]) < float(self.params["PH_MIN"]):
				logging.info("Turning on PHUP pump for 3 seconds")
				await self.execute_cmd("phu")
				logging.info("Turning on MAIN pump for 5 minutes / 40 Liters")
				await self.execute_cmd("mp")
				logging.info("Turning off MAIN pump for 5 minutes  / until waterlevel sensor detects water")
				await self.execute_cmd("mp")

			if float(args["ph"]) > float(self.params["PH_MAX"]):
				logging.info("Turning on PHDWN pump for 3 seconds")
				await self.execute_cmd("phd")
				logging.info("Turning on MAIN pump for 5 minutes / 40 Liters")
				await self.execute_cmd("mp")
				logging.info("Turning off MAIN pump for 5 minutes  / until waterlevel sensor detects water")
				await self.execute_cmd("mp")

async def main():
	with open('/app/param.json') as json_file:
		param = json.load(json_file)
		svc = Hydro('hydro', 'controls', ['readings'], ['update'], redis.Redis(host='redis', port=6379, decode_responses=False), Pusher("hydro", PUSH_GATEWAY_ADDR, grouping_key={"instance": 'hydro'}), param['Cucumber']["Stage1"])
		loop.create_task(svc.listen())

if __name__ == '__main__':
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  logging.info(f"Starting...")
  loop.create_task(main())
  loop.run_forever()
