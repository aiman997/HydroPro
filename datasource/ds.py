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

URL = 'http://10.243.199.34:5000'
redis = aioredis.from_url("redis://redis", db=1)
logging.basicConfig(level=logging.DEBUG)
pubsub = redis.pubsub()
STOPWORD = "STOP"

async def Pgfetch(query):
    while True:
        try:
            async with async_timeout.timeout(1):
                conn = await asyncpg.connect(host='postgres', database='hydrodb', user='postgres', password='eamon2hussien')
                result = await conn.fetch(query)
                if result is not None:
                    await conn.close()
                    return result
        except Exception as e:
            logging.warning('FROM POSTGRES' + e)

async def record(res):
    try:
        logging.info(res)
        values = "now()"
        for x in ("PH_State", "PH_Reading", "EC_State", "EC_Reading", "TEMP_State", "TEMP_Reading", "WL_State", "WL_Reading", "MPUMP_State", "ECUP_State", "PHUP_State", "PHDWN_State"):
            values +=  "," + str(res[x])
        query = f'INSERT INTO hydro.hydrotable (TIMEZ, STATUS_PH, READING_PH, STATUS_EC, READING_EC, STATUS_TEMP, READING_TEMP,  STATUS_WLEVEL, READING_WLEVEL, STATUS_MPUMP, STATUS_ECUP, STATUS_PHUP, STATUS_PHDOWN) VALUES ({values})'
        await Pgfetch(query)
    except Exception as e:
        logging.warning('ERROR WHILE RECORDING DATA: '+e)

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

async def appendkeys(res_dct):
    prefix = ''
    for prefix in res_dct.keys():
        res = await redis.set('Plant::Data::'+prefix, json.dumps(str(res_dct[prefix])))
        logging.info(f'Setting Plant::Data::{prefix} result {res}')

async def processdata():
    try:
        res_str = await fetch('/Tick')
        logging.info("This is fetch res" + res_str)
        if res_str is not None:
            res_dct = json.loads(res_str)#converts the json string to a python dictonary 
            await appendkeys(res_dct)
            logging.info("passed appendkeys")
            await redis.set('Plant::Data', json.dumps(res_dct))
            logging.info('PUBLISHED Plant::Data \t' + time.strftime("%I:%M:%S %p ", time.localtime()) + json.dumps(res_dct, indent=4))
            await record(res_dct)
        else:
            sys.exit('No data to process')
    except Exception as e:
        logging.warning('ERROR WHILE PROCESSING DATA: '+str(e))


async def reader(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    if message["data"].decode() == STOPWORD:
                        logging.info('ds GOT:'+message["data"].decode())
                        break
                    else:
                        logging.info('ds GOT:'+message["data"].decode())
                        return await processdata()
                        #logging.info("Passed Processdata")
                await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            await redis.publish("Plant::RControls", STOPWORD)
            pass

async def main():
    while (1):
        await pubsub.psubscribe("Plant::RControls")
        future = asyncio.create_task(reader(pubsub))
        #await processdata()
        #await asyncio.sleep(1000)
        await future

if __name__ == '__main__':
    asyncio.run(main())
