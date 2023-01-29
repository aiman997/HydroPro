import os
import asyncio
import logging
import redis.asyncio as redis
from lib.service import Service
from aioprometheus import Gauge
from aioprometheus.pusher import Pusher

PREFIX = "HYDRO::USER::"
PUSH_GATEWAY_ADDR = "http://prometheus-push-gateway:9091"

logging.basicConfig(level=logging.INFO)

class Users(Service):
		def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider):
			Service.__init__(self, name, stream, streams, actions, redis_conn, metrics_provider)
			self.newusers_metric = Gauge("newusers", "Users registered")

		async def handel_event(self, event):
			try:
				if 'newuser' in event.keys():
					logging.info(f"newuser event")
				elif 'authuser' in event.keys(): 
					logging.info(f"authuser event")
				elif 'resetuser' in event.keys(): 
					logging.info(f"resetuser event")
				elif 'deluser' in event.keys(): 
					logging.info(f"deluser event")
				else:
					logging.error(f"Error: Invalid event")
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
  loop.create_task(main())
  loop.run_forever()