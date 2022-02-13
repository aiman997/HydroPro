import os
import sys
import time
import re
import json
import asyncio
import logging
import aiohttp
import aioredis
import async_timeout

URL = 'http://10.243.199.34:5000'
redis = aioredis.from_url("redis://redis", db=1)
pubsub = redis.pubsub()
logging.basicConfig(level=logging.DEBUG)
STOPWORD = "STOP"

async def fetch(route):
    async with aiohttp.ClientSession() as session:
        try:
            async with async_timeout.timeout(5):
                resp = await session.get(URL+route)
                response = await resp.text()
                if response is not None:
                    return response
        except Exception as e:
            logging.warning('ERROR WHILE FETCHING DATA: '+str(e))

async def reader(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    if message["data"].decode() == STOPWORD:
                        break
                    else:
                        return await fetch(message["data"].decode())
                await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            pass

async def main():
    pubsub = redis.pubsub()
    await pubsub.psubscribe("Plant::Controls")
    future = asyncio.create_task(reader(pubsub))
    await redis.publish("Plant::Controls", STOPWORD)
    await future

if __name__ == "__main__":
    asyncio.run(main())


