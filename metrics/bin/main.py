import os
import asyncio
import logging
import redis.asyncio as redis
from lib.service import Service
from aioprometheus import Gauge
from aioprometheus.pusher import Pusher

PREFIX = "HYDRO::PLANT"
IP = os.environ.get('IP')
PORT = os.environ.get('PORT')
PUSH_GATEWAY_ADDR = "http://prometheus-push-gateway:9091"

logging.basicConfig(level=logging.INFO)

class Metrics(Service):
		def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider):
			Service.__init__(self, name, stream, streams, actions, redis_conn, metrics_provider)
			self.readings_metric = Gauge("readings", "Sensor readings")
			self.controls_metric = Gauge("controls", "Motor controls")
  
		async def handel_event(self, event):
			try:
				if 'command' in event.keys():
					self.controls_metric.set({'type': event['command']}, float(0))
					self.controls_metric.inc({'type': event['command']})
				else:
					for k in event.keys():
						self.readings_metric.set({'type': k}, float(event[k]))
			except Exception as e:
				logging.error(f"Error: {e}")
			await self.send_event('pushed', event)
  
async def main():
  svc = Metrics('metric', 'metrics', ['readings', 'controls'], ['update'], redis.Redis(host='redis', port=6379, decode_responses=False), Pusher("metric", PUSH_GATEWAY_ADDR, grouping_key={"instance": 'metric'}))
  loop.create_task(svc.listen())

if __name__ == '__main__':
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  logging.info(f"Starting...")
  loop.create_task(main())
  loop.run_forever()