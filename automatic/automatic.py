import os
import re
import sys
import time
import sched
import json
import asyncio
import aiohttp
import logging
import aioredis
import async_timeout
import logging
import requests

logging.basicConfig(level=logging.INFO)

class Automatic:
    def __init__(self, args: dict):
        self.last = time.time()
        if args['api_url']: self.URL = args['api_url']
        if args['redis_url']:
            self.redis = aioredis.from_url(args['redis_url'], db=1)
            self.pubsub = redis.pubsub()
        if args['params']:
            self.params = args['params']

    async def get(self, session: aiohttp.ClientSession, sensor: str, **kwargs):
        url = self.URL+sensor
        resp = await session.request('GET', url=url, **kwargs)
        data = await resp.json()
        return data

    async def get_params(self, args, **kwargs):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for c in args:
                tasks.append(self.get(session=session, sensor=c, **kwargs))
            res = await asyncio.gather(*tasks, return_exceptions=True)
            return res
    
    async def execute_cmd(self, command):
        async with aiohttp.ClientSession() as session:
            logging.info("Executing  " + str(command))
            url = self.URL+command
            resp = await session.request('GET', url=url)
            data = await resp.json()
            return data
        

    async def adjust(self, args):
        ec = 10
        ph = 1.0
        i = 0
        for i in range(10):
            logging.info("loop: ")
            logging.info(i)
            ec = ec + 40
            ph = ph + 0.5
        # dct = {}
        # for list_dict in args:
        #     dct.update(list_dict)
       

            logging.info("cuurent ec")
            logging.info(ec)


            dct = {"ec":ec, "ph": ph}

            logging.info("dct: " + str(dct))
            logging.info("params: " + str(self.params))
            

            if dct["ec"] < float(self.params["EC_MIN"]):
                logging.info("Turning on ECUP pump for 3 seconds")
                await self.execute_cmd("pec")
                logging.info("Turning on MAIN pump for 5 minutes / 40 Liters")
                await self.execute_cmd("mp")
                logging.info("Turning off MAIN pump for 5 minutes  / until waterlevel sensor detects water")
                await self.execute_cmd("mp")
               

                    
            elif dct["ec"] > float(self.params["EC_MAX"]):
                logging.info("Turning on Solenoid Valve Out for 2 minutes / 10 Liters")
                await self.execute_cmd("svo")
                logging.info("Turning off Solenoid Valve OUT")
                await self.execute_cmd("svo")
                logging.info("Turning on Solenoid Valve In for 2 minutes / 10 Liters / Until waterlevel sensor detects water")
                await self.execute_cmd("svi")
                logging.info("Turning on MAIN pump for 5 minutes / 40 Liters")
                await self.execute_cmd("mp")
                logging.info("Turning off MAIN pump for 5 minutes  / until waterlevel sensor detects water")
                await self.execute_cmd("mp")
               
            
            elif dct["ph"] < float(self.params["PH_MIN"]):
                logging.info("Turning on PHUP pump for 3 seconds")
                await self.execute_cmd("phu")
                logging.info("Turning on MAIN pump for 5 minutes / 40 Liters")
                await self.execute_cmd("mp")
                logging.info("Turning off MAIN pump for 5 minutes  / until waterlevel sensor detects water")
                await self.execute_cmd("mp")

            elif dct["ph"] > float(self.params["PH_MAX"]):
                logging.info("Turning on PHDWN pump for 3 seconds")
                await self.execute_cmd("phd")
                logging.info("Turning on MAIN pump for 5 minutes / 40 Liters")
                await self.execute_cmd("mp")
                logging.info("Turning off MAIN pump for 5 minutes  / until waterlevel sensor detects water")
                await self.execute_cmd("mp")
        
            else: 
                return "Optimum"
            
        return dct

    async def run(self):
        while True:
            try:
                params = await self.get_params(['ec','ph','tp', 'wl', 'wf'])
                result = await self.adjust(params)
                logging.info("result")
                logging.info(result)
                await asyncio.sleep(15)
            except Exception as e:
                logging.warning(e)

if __name__ == "__main__":
    with open('/home/flask/app/automatic/param.json') as json_file:
        param = json.load(json_file)
        at = Automatic({"api_url": "http://10.243.199.34:8008/", "params": param['Cucumber']["Stage1"], "redis_url": None})
        asyncio.run(at.run())
