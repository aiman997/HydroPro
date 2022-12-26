import asyncio
import async_timeout
import time
import json
import logging
import redis.asyncio as redis
import aiohttp
import websockets
import os
#from dotenv import load_dotenv

#load_dotenv()

PREFIX = "HYDRO::PLANT"
IP = os.environ.get('IP')
PORT = os.environ.get('PORT')
READING_DURATION = '15'

logging.basicConfig(level=logging.INFO)

class RPI:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.ws_url = f"ws://{ip}:{port}/ws/"
        self.redis = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.channel_name = f"{PREFIX}::{ip}::CONTROLS"

    async def publish_readings(self, readings):
        readings['time'] = time.time()
        logging.info(f"Publishing readings at {time.time()}: {readings}")
        try:
            await self.redis.xadd(name=f"{PREFIX}::{IP}::READINGS", fields=readings, id='*', maxlen=100, approximate=True, nomkstream=False, minid=None, limit=None)
        except Exception as e:
            logging.error(e)

    async def handel_readings(self):
        ws = await websockets.connect(f'ws://{self.ip}:{self.port}/ws/all')
        while True:
            logging.info(f"Trying readings...")
            try:
                await ws.send(READING_DURATION)
                async with async_timeout.timeout(int(READING_DURATION)):
                    res = await ws.recv()
                    logging.info(res)
                    readings = json.loads(res)
                    if readings:
                        await self.publish_readings(readings)
            except (asyncio.TimeoutError, json.decoder.JSONDecodeError) as e:
                logging.error(e)
            await asyncio.sleep(10)

    async def handel_controls(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.channel_name+'::AUTOMATIC', self.channel_name+'::MANUAL')
        while True:
            logging.info(f"Trying controls...")
            try:
                async with async_timeout.timeout(1):
                    message = await pubsub.get_message()
                    if message and message["type"] == "message":
                        payload = json.loads(message["data"])
                        # TODO: async def validate_control()
                        logging.debug(f"Payload is: {payload}")
                        await self.publish_control(payload["param"], payload["duration"])
            except (asyncio.TimeoutError, json.decoder.JSONDecodeError) as e:
                logging.error(f"Error while handeling controls: {e}")
            await asyncio.sleep(10)

    async def publish_control(param: str, duration: int):
        logging.debug(f"Sending message to control {param}: {duration}")
        await asyncio.sleep(0.2)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    pi = RPI(IP, PORT)
    logging.info(f"Starting...")
    loop.create_task(pi.handel_controls())
    loop.create_task(pi.handel_readings())
    loop.run_forever()