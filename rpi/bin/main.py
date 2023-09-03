import asyncio
import async_timeout
import time
import json
import logging
import redis.asyncio as redis
import os
from lib.service import Service
from aioprometheus.pusher import Pusher

PREFIX = "HYDRO::PLANT"
PUSH_GATEWAY_ADDR = os.environ.get('PUSH_GATEWAY_ADDR')

logging.basicConfig(level=logging.INFO)

class RPI(Service):
    def __init__(self, name, stream, streams, actions, redis_conn, metrics_provider):
        Service.__init__(self, name, stream, streams, actions, redis_conn, metrics_provider)
        self.rpcs.append('read')

    @Service.rpc
    async def read(self, event):
        logging.info(event)
        try:
            return {"success": 1, "status": "reading"}
        except Exception as e:
            logging.error(f"Error while read: {e}")
            return {"error": 1, "message": e }

    async def handle_event(self, event):
        logging.info(f"Handling event: {event}")
        try:
            if 'command' in event.keys():
                logging.info(f"Sending message to control: {event}")
                await self.send_event('update', json.loads(event))
        except Exception as e:
            logging.error(f"Error: {e}")
        logging.info(f"Event handled successfully")

async def main():
    svc = RPI('rpi', 'rpi', ['api'], ['ping', 'update', 'read', 'add', 'remove'], redis.Redis(host='redis', port=6379, decode_responses=False), Pusher("rpi", PUSH_GATEWAY_ADDR, grouping_key={"instance": 'rpi'}))
    loop.create_task(svc.listen())

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logging.info(f"Starting...")
    loop.run_until_complete(main())
    loop.run_forever()
