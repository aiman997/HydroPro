from flask import Flask, redirect, url_for, request, render_template, make_response
from datetime import datetime
import time
import sys
import os
import re
import pprint
import json
import logging
import asyncio
import asyncpg
import aioredis
import aiohttp

URL = 'http://10.243.199.34:5000'
Path = ""
res_dct = ()

app = Flask(__name__)
redis = aioredis.from_url("redis://redis", db=1)
pubsub = redis.pubsub()

# Configure Logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

async def fetch(Path):
    logging.warning("IM IN fetch")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(URL + Path) as resp:
                keyvalues = await resp.text()
                logging.warning(resp)
		        # logging.warning(keyvalues)
                return keyvalues
        except Exception as e:
            logging.warning(e)

async def Pgfetch(query):
    conn = await asyncpg.connect(host='postgres', database='hydrodb', user='postgres', password='eamon2hussien')
    result = await conn.fetch(query)
    await conn.close()
    return result

@app.route('/')
async def base():
    return render_template('base.html')

@app.route('/Dashboard')
async def dashboard():
#    try:
#        data = await redis.get("Plant::Data")
#        if data is not None:
#            logging.info(json.loads(data.decode('utf-8')))
#    except Exception as e:
#        logging.info(e)
# here we need a graph/
    return render_template('Dashboard.html')

@app.route('/Cards')
async def cards():
    return render_template('cards.html')

@app.route('/database')
async def datab():
    result = await Pgfetch('''SELECT * FROM hydro.hydrotable order by ID''')
    return render_template("database.html", result=result)

@app.route('/ControlPanel', methods=['GET', 'POST'])
async def index():
    PH_Reading = await Pgfetch('''SELECT READING_PH FROM hydro.hydrotable LIMIT 1''')
    PHREADING = re.findall("\=(.*)\>", str(PH_Reading))
    logging.warning(PH_Reading)
    logging.warning(PHREADING)

    EC_Reading = await Pgfetch('''SELECT READING_PH FROM hydro.hydrotable LIMIT 1''')
    ECREADING = re.findall("\=(.*)\>", str(EC_Reading))
    logging.warning(EC_Reading)
    logging.warning(ECREADING)

    if request.method == 'POST':
        if request.form.get('PH_ON') == 'PH_ON':
            await redis.publish("Plant::Control", '{"W":"true"}')
            res_dct = await fetch('/PHon')
            logging.warning(res_dct)

        elif request.form.get('PH_OFF') == 'PH_OFF':
            await redis.publish("Plant::Controls", '{"action": "POFF"}')
            res_dct = await fetch('/PHoff')
            logging.warning(res_dct)

        elif request.form.get('EC_ON') == 'EC_ON':
            await redis.publish("Plant::Controls", '{"action": "PHdownON"}')

        elif request.form.get('EC_OFF') == 'EC_OFF':
            await redis.publish("Plant::Controls", '{"action": "EC_OFF"}')

        elif request.form.get('PHdown_OFF') == 'PHdown_OFF':
            await redis.publish("Plant::Controls", '{"action": "PHdownOFF"}')

        elif request.form.get('EC_ON') == 'EC_ON':
            await redis.publish("Plant::Controls", '{"action": "ECON"}')

        elif request.form.get('EC_OFF') == 'EC_OFF':
            await redis.publish("Plant::Controls", '{"action": "ECOFF"}')

        elif request.form.get('TempSensor_ON') == 'TempSensor_ON':
            await redis.publish("Plant::Controls", '{"action": "TempON"}')

        elif request.form.get('TempSensor_OFF') == 'TempSensor_OFF':
            await redis.publish("Plant::Controls", '{"action": "TempOFF"}')

    elif request.method == 'GET':
        print("No Post Back Call")

    return render_template("index.html", PHREADING=PHREADING , ECREADING=ECREADING)


if __name__ == '__main__':
    app.run(debug = True)
