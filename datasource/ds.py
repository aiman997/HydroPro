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

URL = 'http://192.168.101.26:80'
redis = aioredis.from_url("redis://redis", db=1)
pubsub = redis.pubsub()
logging.basicConfig(level=logging.INFO)

async def Pgfetch(query):
    conn = await asyncpg.connect(host='postgres', database='hydrodb', user='postgres', password='eamon2hussien')
    result = await conn.fetch(query)
    await conn.close()
    return result

async def record(res):
    values = 'now()'
    for x in ('PH_Status', 'PH_Reading', 'EC_Status', 'EC_Reading', 'TEMP_Status', 'TEMP_Reading', 'PUMP_Status', 'ECUP_Status', 'PHUP_Status', 'PHDOWN_Status'):
        values +=  ', ' + res[x]
    query = f'INSERT INTO hydro.hydrotable (TIMEZ, STATUS_PH, READING_PH, STATUS_EC, READING_EC, STATUS_TEMP, READING_TEMP, STATUS_MPUMP, STATUS_ECUP, STATUS_PHUP, STATUS_PHDOWN) VALUES ({values})'
    await Pgfetch(query)

async def fetch():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(URL, data = '{"action": "waterON"}') as resp:
                keyvalues = await resp.text()
                values = re.findall("\{(.*?)\}", keyvalues)
                result = []
                for row in values:
                    x = row.split(',')
                    for column in x:
                        key_value_pairs = column.split(':')
                        result += key_value_pairs
                res_dct = {result[i]: result[i + 1] for i in range(0, len(result), 2)}
                return res_dct
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
    while (1):
        res_dct = await fetch()
        await redis.set('Plant::Data', json.dumps(res_dct))
        logging.warning('PUBLISHED Plant::Data' + time.strftime("%I:%M:%S %p ", time.localtime()) + json.dumps(res_dct, indent = 4))
        await record(res_dct)
        await sub()
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
