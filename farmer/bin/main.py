import asyncio
import async_timeout
import time
import json
import logging
import redis.asyncio as redis
import websockets
import os
from lib.service import Service
from aioprometheus.pusher import Pusher

PREFIX = "HYDRO::PLANT"
IP = os.environ.get('IP')
PORT = os.environ.get('PORT')
READING_DURATION = '15'
SLEEP_DURATION = 10
PUSH_GATEWAY_ADDR = "http://prometheus-push-gateway:9091"

logging.basicConfig(level=logging.INFO)

class RPI(Service):
	def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider):
		Service.__init__(self, name, stream, streams, actions, redis_conn, metrics_provider)

	async def handel_readings(self):
		async for websocket in websockets.connect(f'ws://{IP}:{PORT}/ws/all'):
			try:
				await websocket.send(READING_DURATION)
				res = await websocket.recv()
				logging.info(f"Received: {type(res)}-{res}")
				await self.send_event('update', json.loads(res))
			except websockets.ConnectionClosed:
				continue
		await asyncio.sleep(SLEEP_DURATION)

	async def handel_event(self, event):
		try:
			if 'command' in event.keys():
				logging.info(f"Sending message to control: {event}")
		except Exception as e:
			logging.error(f"Error: {e}")

async def main():
	svc = RPI('rpi', 'readings', ['controls'], ['update'], redis.Redis(host='redis', port=6379, decode_responses=False), Pusher("rpi", PUSH_GATEWAY_ADDR, grouping_key={"instance": 'rpi'}))
	loop.create_task(svc.listen())
	loop.create_task(svc.handel_readings())

if __name__ == '__main__':
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	logging.info(f"Starting...")
	loop.create_task(main())
	loop.run_forever()
