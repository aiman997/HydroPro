import os
import re
import sys
import time
import json
import asyncio
import logging
import aioredis
import async_timeout

URL = 'http://10.243.199.34:5000'
redis = aioredis.from_url("redis://redis", db=1)
pubsub = redis.pubsub()
logging.basicConfig(level=logging.INFO)
STOPWORD = "STOP"
 
async def get_StartTime():
    curr_time = time.strftime("%H:%M:%S", time.localtime())
    logging.info("Current Time is :" +  curr_time)

async def reader(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    if message["data"].decode() == STOPWORD:
                        logging.info('Stopped' + message["data"].decode())
                        break
                    else:
                        logging.info('Got: ' +message["data"].decode())
                        return await get_StartTime()
                    await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            await redis.publish("Plant::Auto", STOPWORD)
            pass

#async def get_PlantType()
#async def get_StageInterval()
#async def get_ParmEC()
#async def get_ParmPH()
#async def get_WakeupInterval()

async def main():
    await pubsub.psubscribe("Plant::Auto")
    future = asyncio.create_task(reader(pubsub))
    await future

if __name__ == "__main__":
    asyncio.run(main())
