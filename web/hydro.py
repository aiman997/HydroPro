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
import random
import io
import base64

app = Flask(__name__)
URL = 'http://10.243.199.34:5000'
redis = aioredis.from_url("redis://redis", db=1)
pubsub = redis.pubsub()
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

async def Pgfetch(query):
    result = None
    while result == None:
        try:
            conn = await asyncpg.connect(host='postgres', database='hydrodb', user='postgres', password='eamon2hussien')
            result = await conn.fetch(query)
            await conn.close()
            return result
        except Exception as e:
            logging.warning('FROM POSTGRES' + e)

async def pubControls (data):
    try:
        return await redis.publish("Plant::Controls", data)
    except Exception as e:
        logging.warning(e)

@app.route('/')
async def base():
    return render_template('base.html')

@app.route('/Dashboard')
async def dashboard():
    PH_Reading = await Pgfetch('''SELECT READING_PH FROM hydro.hydrotable LIMIT 1''')
    PHREADING = re.findall("\=(.*)\>", str(PH_Reading))
    logging.warning(PH_Reading)
    logging.warning(PHREADING)

    EC_Reading = await Pgfetch('''SELECT READING_PH FROM hydro.hydrotable LIMIT 1''')
    ECREADING = re.findall("\=(.*)\>", str(EC_Reading))
    logging.warning(EC_Reading)
    logging.warning(ECREADING)

#    try:
#        data = await redis.get("Plant::Data")
#        if data is not None:
#            logging.info(json.loads(data.decode('utf-8')))
#    except Exception as e:
#        logging.info(e)
# here we need a graph/
    return render_template('card.html')


@app.route("/superplot", methods=["GET"])
async def plotView():
    timeInterval = 7;
    query = ('''SELECT TIMEZ, count(DISTINCT(READING_PH))
                      from hydro.hydrotable
                      WHERE TIMEZ >
                      (current_timestamp - INTERVAL '7 days')
                      GROUP BY TIMEZ ORDER BY TIMEZ;''')
    try:
        result = await Pgfetch(query)
    except Exception as e:
        logging.warning(e)

    for rec in result:
        tses.append(rec[0])
        ucounts.append(rec[1])

    return render_template("plot.html", data=ucounts)


@app.route('/Plot')
async def plot():
    timeInterval = 7;
    ucounts = []
    query ='''SELECT tstampz, count(DISTINCT(id))
                from hydro
                WHERE tstampz >
                (current_timestamp - INTERVAL '7 days')
                GROUP BY tstampz ORDER BY tstampz;'''
    result = Pgfetch(query)
    for rec in result:
        tses.append(rec[0])
        ucounts.append(rec[1])

    return render_template('Dashboard.html')

@app.route('/Cards')
async def cards():
    return render_template('cards.html')

@app.route('/database')
async def datab():
    result = await Pgfetch('''SELECT * FROM hydro.hydrotable order by ID desc LIMIT 100''')
    return render_template("database.html", result=result)

@app.route('/ControlPanel', methods=['GET', 'POST'])
async def index():
    if request.method == 'POST':
        logging.critical("index")
        if request.form.get('PH_ON') == 'PH_ON':
            await pubControls('/PHon')

        elif request.form.get('PH_OFF') == 'PH_OFF':
            await pubControls('/PHoff')

        elif request.form.get('PH_READ') == 'PH_READ':
            await pubControls('/ECPHRead')

        elif request.form.get('EC_ON') == 'ON':
            await pubControls('/ECon')

        elif request.form.get('EC_OFF') == 'OFF':
            await pubControls('/ECoff')

        elif request.form.get('EC_READ') == 'READ':
            await pubControls('/ECRead')

        elif request.form.get('TEMP_ON') == 'TEMP_ON':
            await pubControls('/TEMPon')

        elif request.form.get('TEMP_OFF') == 'TEMP_OFF':
            await pubControls('/TEMPoff')

        elif request.form.get('TEMP_READ') == 'TEMP_READ':
            await pubControls('/TEMPRead')

        elif request.form.get('WL_ON') == 'WL_ON':
            await pubControls('/WLon')

        elif request.form.get('WL_OFF') == 'WL_OFF':
            await pubControls('/WLoff')

        elif request.form.get('WL_READ') == 'WL_READ':
            await pubControls('/WLRead')

        elif request.form.get('MPUMP_ON') == 'MPUMP_ON':
            await pubControls('/MPUMPon')

        elif request.form.get('MPUMP_OFF') == 'MPUMP_OFF':
            await pubControls('/MPUMPoff')

        elif request.form.get('ECUP_ON') == 'ECUP_ON':
            await pubControls('/ECUPon')

        elif request.form.get('ECUP_OFF') == 'ECUP_OFF':
            await pubControls('/ECUPoff')

        elif request.form.get('PHUP_ON') == 'PHUP_ON':
            await pubControls('/PHUPon')

        elif request.form.get('PHUP_OFF') == 'PHUP_OFF':
            await pubControls('/PHUPoff')

        elif request.form.get('PHDWN_ON') == 'PHDWN_ON':
            await pubControls('/PHDWNon')

        elif request.form.get('PHDWN_OFF') == 'PHDWN_OFF':
            await pubControls('/PHDWNoff')

    elif request.method == 'GET':
        print("No Post Back Call")
    return render_template("index.html", PHREADING=101 , ECREADING=101)


if __name__ == '__main__':
    app.run(debug = True)
