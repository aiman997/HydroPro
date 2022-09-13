from flask import Flask, redirect, url_for, request, render_template, make_response
from datetime import datetime
import time
import sys
import os
import re
import pprint
import json
import logging
import redis
import random
import io
import base64
import psycopg2

app = Flask(__name__)
URL = 'http://10.243.199.34:5000'
redis = redis.from_url("redis://redis", db=1) #create a connection
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

def Pgfetch(query):
    while True:
        try:
            conn = psycopg2.connect(host='postgres', database='hydrodb', user='postgres', password='eamon2hussien')
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            if result is not None:
                conn.close()
                return result
        except Exception as e:
            logging.warning('FROM POSTGRES' +str(e))

def pubControls (data):
    try:
        redis.publish("Plant::Controls", data)
    except Exception as e:
        logging.warning("WHILE PUBLISHING CONTROLS"+str(e))

def pubRControls (data):
    try:
        redis.publish("Plant::RControls", data)
    except Exception as e:
        logging.warning("WHILE PUBLISHING RCONTROLS" + str(e))

def pubAutoControl (data):
    try:
        redis.publish("Plant::Auto", data)
    except Exception as e:
        logging.warning("WHILE PUBLISHSING AUTO" + str(e))

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/database')
def datab():
    result = Pgfetch('''SELECT * FROM hydro.hydrotable order by ID desc LIMIT 100''')
    return render_template("database.html", result=result)

@app.route('/Settings')
def settings():
    return render_template("settings.html")

@app.route('/Cards')
def cards():
    return render_template('cards.html')

@app.route('/ControlPanel', methods=['GET', 'POST'])
def index():
    PH_Reading = Pgfetch('''SELECT READING_PH FROM hydro.hydrotable ORDER BY ID DESC LIMIT 1''')
    PH_Reading = str(PH_Reading)
    slice_PHREADING = slice(2,7)
    PHREADING = PH_Reading[slice_PHREADING]
    logging.warning(PH_Reading)
    logging.warning(PHREADING)

    PH_State = Pgfetch('''SELECT STATUS_PH FROM hydro.hydrotable ORDER BY ID DESC LIMIT 1''')
    PH_State = str(PH_State)
    slice_PHSTATE = slice(3,7)
    PHSTATE = PH_State[slice_PHSTATE]

    EC_Reading = Pgfetch('''SELECT READING_EC FROM hydro.hydrotable ORDER BY ID DESC LIMIT 1''')
    ECREADING = re.findall("\=(.*)\>", str(EC_Reading))
    EC_Reading = str(EC_Reading)
    slice_ECREAD = slice(2,7)
    ECREADING = EC_Reading[slice_ECREAD]
    logging.warning(EC_Reading)
    logging.warning(ECREADING)
    
    EC_State = Pgfetch('''SELECT STATUS_EC FROM hydro.hydrotable ORDER BY ID DESC LIMIT 1''')
    EC_State = str(EC_State)
    slice_ECSTATE = slice(3,7)
    ECSTATE = EC_State[slice_PHSTATE]
    
    if request.method == 'POST':
        if request.form.get('PH_ON') == 'PH_ON':
            pubControls('/PHon')

        elif request.form.get('PH_OFF') == 'PH_OFF':
            pubControls('/PHoff')

        elif request.form.get('PH_READ') == 'PH_READ':
            pubControls('/PHread')
            time.sleep(5)
            pubRControls('/PHread')

        elif request.form.get('EC_ON') == 'EC_ON':
            pubControls('/ECon')

        elif request.form.get('EC_OFF') == 'EC_OFF':
            pubControls('/ECoff')

        elif request.form.get('EC_READ') == 'EC_READ':
            pubControls('/ECread')
            pubRControls('/ECread')

        elif request.form.get('TEMP_ON') == 'TEMP_ON':
            pubControls('/TEMPon')

        elif request.form.get('TEMP_OFF') == 'TEMP_OFF':
            pubControls('/TEMPoff')

        elif request.form.get('TEMP_READ') == 'TEMP_READ':
            pubControls('/TEMPread')
            pubRControls('/TEMPRead')

        elif request.form.get('MPUMP_ON') == 'ON':
            pubControls('/MPUMPon')
        
        elif request.form.get('MPUMP_OFF') == 'OFF':
            pubControls('/MPUMPoff')

        elif request.form.get('AUTO') == 'AUTO':
            pubAutoControl('/Auto')
            
    elif request.method == 'GET':
        print("No Post Back Call")
    
    
    return render_template("index.html", PHREAD=PHREADING, PHSTATE=PHSTATE, ECREAD=ECREADING, ECSTATE=ECSTATE)


if __name__ == '__main__':
    app.run(debug = True)
