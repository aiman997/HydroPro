import os
import sys
import time
import re
import json
import asyncio
import logging
import aiohttp
import asyncpg
import aioredis
import async_timeout

URL = 'http://10.243.199.34:5000/PHon'
redis = aioredis.from_url("redis://redis", db=1)
pubsub = redis.pubsub()
logging.basicConfig(level=logging.INFO)

async def Pgfetch(query):
    conn = await asyncpg.connect(host='postgres', database='hydrodb', user='postgres', password='eamon2hussien')
    result = await conn.fetch(query)
    await conn.close()
    return result #to where?

async def record(res):
    values = 'now()'
    for x in ('PH_S', 'PH_R', 'EC_S', 'EC_R', 'TEMP_S', 'TEMP_R', 'PUMP_S', 'ECUP_S', 'PHUP_S', 'PHDOWN_S'):
        values +=  ', ' + res[x]
    query = f'INSERT INTO hydro.hydrotable (TIMEZ, STATUS_PH, READING_PH, STATUS_EC, READING_EC, STATUS_TEMP, READING_TEMP, STATUS_MPUMP, STATUS_ECUP, STATUS_PHUP, STATUS_PHDOWN) VALUES ({values})'
    await Pgfetch(query)

async def fetch():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(URL) as resp:
                keyvalues = await resp.text()
                logging.warning(resp)
		        # logging.warning(keyvalues)
                return keyvalues
        except Exception as e:
            logging.warning(e)

async def sub():
    await pubsub.subscribe("Plant::Controls")
    x = await pubsub.get_message()
    if x is None:
        logging.info('Empty data from controls')
    elif x.get('data') != 1:
        logging.critical(x.get('data'))

res_dct = ()
async def main():
    logging.info('I am up...')
    while (1):
        res_dct = await fetch()
        logging.info(res_dct)
        # await redis.set('Plant::Data', json.dumps(res_dct))
        # logging.warning('PUBLISHED Plant::Data' + time.strftime("%I:%M:%S %p ", time.localtime()) + json.dumps(res_dct, indent = 4))
        # await record(res_dct)
        # await sub()
        logging.info('Night...')
        await asyncio.sleep(60)
        logging.info('Done sleeping...')

if __name__ == '__main__':
    asyncio.run(main())
