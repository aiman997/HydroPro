from flask import Flask, redirect, url_for, request, render_template, make_response
from datetime import datetime
import time
import sys
import os
import re
import pprint
import json
import logging
import redis #aioredisu
import random
import io
import base64
import psycopg2

app = Flask(__name__)
URL = 'http://10.243.199.34:5000'
redis = redis.from_url("redis://redis", db=1)#create a connection)
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

#def record (value_recieved):
#    try:
#        logging.info(value_recieved)
#        values = "now()"
#        for x in ("PH_State", "PH_Reading", "EC_State", "EC_Reading", "TEMP_State", "TEMP_Reading", "WL_State", "WL_Reading", "MPUMP_State", "ECUP_State", "PHUP_State", "PHDWN_State");
#            values += "," + str(value_recieved[x])
#        query = f'INSERT INTO hydro.hydrotable (TIMEZ, STATUS_PH, READING_PH, STATUS_EC, READING_EC, STATUS_TEMP, READING_TEMP, STATUS_WLEVEL, READING_WLEVEL, STATUS_MPUMP, STATUS_ECUP, STATUS_PHUP, STATUS_PHDWN, )
        

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/database')
def datab():
    result = Pgfetch('''SELECT * FROM hydro.hydrotable order by ID desc LIMIT 100''')
    return render_template("database.html", result=result)


@app.route('/Dashboard') 
def dashboard():
    PH_Reading = Pgfetch('''SELECT READING_PH FROM hydro.hydrotable LIMIT 1''')
    PHREADING = re.findall("\=(.*)\>", str(PH_Reading))
    logging.warning(PH_Reading)
    logging.warning(PHREADING)

    EC_Reading = Pgfetch('''SELECT READING_PH FROM hydro.hydrotable LIMIT 1''')
    #ECREADING = re.findall("\=(.*)\>", str(EC_Reading))
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
def plotView():
    timeInterval = 7;
    query = ('''SELECT TIMEZ, count(DISTINCT(READING_PH))
                      from hydro.hydrotable
                      WHERE TIMEZ >
                      (current_timestamp - INTERVAL '7 days')
                      GROUP BY TIMEZ ORDER BY TIMEZ;''')
    try:
        result = Pgfetch(query)
    except Exception as e:
        logging.warning(e)

    for rec in result:
        tses.append(rec[0])
        ucounts.append(rec[1])

    return render_template("plot.html", data=ucounts)


@app.route('/Plot')
def plot():
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
def cards():
    return render_template('cards.html')

@app.route('/ControlPanel', methods=['GET', 'POST'])
def index():
    PH_Reading = Pgfetch('''SELECT READING_PH FROM hydro.hydrotable ORDER BY ID DESC LIMIT 1''')
    #PHREADING = re.findall("\=(.*)\>", str(PH_Reading))
    PH_Reading = str(PH_Reading)
    slice_PHREADING = slice(2,7)
    PHREADING = PH_Reading[slice_PHREADING]
    logging.warning(PH_Reading)
    logging.warning(PHREADING)

    PH_State = Pgfetch('''SELECT STATUS_PH FROM hydro.hydrotable ORDER BY ID DESC LIMIT 1''')
    PH_State = str(PH_State)
    slice_PHSTATE = slice(3,7)
    PHSTATE = PH_State[slice_PHSTATE]
    
    #result = re.search('((.*))', s)
    #PHSTATE = result.group(1)
    #print(result.group(1))

    EC_Reading = Pgfetch('''SELECT READING_EC FROM hydro.hydrotable ORDER BY ID DESC LIMIT 1''')
    ECREADING = re.findall("\=(.*)\>", str(EC_Reading))
    EC_Reading = str(EC_Reading)
    slice_ECREAD = slice(2,7)
    ECREADING = EC_Reading[slice_ECREAD]
    logging.warning(EC_Reading)
    logging.warning(ECREADING)
    
    EC_State = Pgfetch('''SELECT STATUS_EC FROM hydro.hydrotable ORDER BY ID DESC LIMIT 1''')
    if request.method == 'POST':
        if request.form.get('PH_ON') == 'PH_ON':
            pubControls('/PHon')

        elif request.form.get('PH_OFF') == 'PH_OFF':
            pubControls('/PHoff')

        elif request.form.get('PH_READ') == 'PH_READ':
            pubControls('/PHread')

        elif request.form.get('EC_ON') == 'EC_ON':
            pubControls('/ECon')

        elif request.form.get('EC_OFF') == 'EC_OFF':
            pubControls('/ECoff')

        elif request.form.get('EC_READ') == 'EC_READ':
            pubControls('/ECread')

        elif request.form.get('TEMP_ON') == 'TEMP_ON':
            pubControls('/TEMPon')

        elif request.form.get('TEMP_OFF') == 'TEMP_OFF':
            pubControls('/TEMPoff')

        elif request.form.get('TEMP_READ') == 'TEMP_READ':
            pubControls('/TEMPread')

        elif request.form.get('MPUMP_ON') == 'ON':
            pubControls('/MPUMPon')
        
        elif request.form.get('MPUMP_OFF') == 'OFF':
            pubControls('/MPUMPoff')

    elif request.method == 'GET':
        print("No Post Back Call")
    
    
    return render_template("index.html", PHREAD=PHREADING, PHSTATE=PHSTATE, ECREAD=ECREADING, ECSTATE=EC_State)


if __name__ == '__main__':
    app.run(debug = True)
