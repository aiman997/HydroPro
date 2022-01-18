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

app = Flask(__name__)
redis = aioredis.from_url("redis://redis", db=1)
pubsub = redis.pubsub()

# Configure Logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

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
    data = await redis.get("Plant::Data")
    if data is not None:
        logging.warning(json.loads(data.decode('utf-8')))
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
    if request.method == 'POST':
        if request.form.get('PHup_ON') == 'PHup_ON':
            await redis.publish("Plant::Controls", '{"action": "PHupON"}')

        elif request.form.get('PHup_OFF') == 'PHup_OFF':
            await redis.publish("Plant::Controls", '{"action": "PHupOFF"}')

        elif request.form.get('PHdown_ON') == 'PHdown_ON':
            await redis.publish("Plant::Controls", '{"action": "PHdownON"}')

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

    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug = True)
