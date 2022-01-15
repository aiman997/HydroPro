from flask import Flask, redirect, url_for, request, render_template, make_response
from datetime import datetime
import logging
import psycopg2
import redis
import sys
import requests
import os
import re
import pprint

app = Flask(__name__)
cache = redis.StrictRedis(host='redis', port=6379)

# Configure Logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

def PgFetch(query, method):

    # Connect to an existing database
    conn = psycopg2.connect("host='postgres' dbname='hydrodb' user='postgres' password='eamon2hussien'")

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Query the database and obtain data as Python objects
    dbquery = cur.execute(query)

    if method == 'GET':
        result = cur.fetchall()
    else:
        result = ""

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()
    return result
@app.route('/')
def base():
    return render_template('base.html')

@app.route('/count')
def hello_world():
    if cache.exists('visitor_count'):
        cache.incr('visitor_count')
        count = (cache.get('visitor_count')).decode('utf-8')
        update = PgFetch("UPDATE visitors set visitor_count = " + count + " where site_id = 1;", "POST")
    else:
        cache_refresh = PgFetch("SELECT visitor_count FROM visitors where site_id = 1;", "GET")
        count = int(cache_refresh[0])
        cache.set('visitor_count', count)
        cache.incr('visitor_count')
        count = (cache.get('visitor_count')).decode('utf-8')
    return 'Hello Linode!  This page has been viewed %s time(s).' % count

@app.route('/resetcounter')
def resetcounter():
    cache.delete('visitor_count')
    PgFetch("UPDATE visitors set visitor_count = 0 where site_id = 1;", "POST")
    app.logger.debug("reset visitor count")
    return "Successfully deleted redis and postgres counters"


@app.route('/database')
def datab():
    conn = psycopg2.connect("host='postgres' dbname='hydrodb' user='postgres' password='eamon2hussien'")

    # Open a cursor to perform database operations
    cur = conn.cursor()

    dbquery = cur.execute('''SELECT * FROM hydro.hydrotable order by ID''')
    result = cur.fetchall()
    cur.close()
    conn.close()
    app.logger.debug(result)
    return render_template("database.html", result=result)



URL = 'http://192.168.101.26:80'

@app.route('/ControlPanel', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('PHup_ON') == 'PHup_ON':
            x = requests.post(URL, data = '{"action": "waterON"}')
            app.logger.debug(x.text)
            keyvalues = x.text
            values = re.findall("\{(.*?)\}", keyvalues)
            result = []
            for row in values:
                x = row.split(',')
                for column in x:
                    key_value_pairs = column.split(':')
                    result += key_value_pairs

            res_dct = {result[i]: result[i + 1] for i in range(0, len(result), 2)}
            query = str ( '''INSERT INTO hydro.hydrotable (
                TIMEZ,
                STATUS_PH,
                READING_PH,
                STATUS_EC,
                READING_EC,
                STATUS_TEMP,
                READING_TEMP,
                STATUS_MPUMP,
                STATUS_ECUP,
                STATUS_PHUP,
                STATUS_PHDOWN
            )
                VALUES (
                now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )'''
            , res_dct['PH_Status']
            , res_dct['PH_Reading']
            , res_dct['EC_Status']
            , res_dct['EC_Reading']
            , res_dct['TEMP_Status']
            , res_dct['TEMP_Reading']
            , res_dct['PUMP_Status']
            , res_dct['ECUP_Status']
            , res_dct['PHUP_Status']
            , res_dct['PHDOWN_Status'] )

            PgFetch(query, "POST")

            x = PgFetch('''SELECT * FROM hydro.hydrotable;''', "GET")
            app.logger.debug(x)

        elif request.form.get('PHup_OFF') == 'PHup_OFF':
            x = requests.post(URL, data = '{"action": "PHupOFF"}')

        elif request.form.get('PHdown_ON') == 'PHdown_ON':
            x = requests.post(URL, data = '{"action": "PHdownON"}')

        elif request.form.get('PHdown_OFF') == 'PHdown_OFF':
            x = requests.post(URL, data = '{"action": "PHdownOFF"}')

        elif request.form.get('EC_ON') == 'EC_ON':
            x = requests.post(URL, data = '{"action": "ECON"}')

        elif request.form.get('EC_OFF') == 'EC_OFF':
            x = requests.post(URL, data = '{"action": "ECOFF"}')

        elif request.form.get('TempSensor_ON') == 'TempSensor_ON':
            x = requests.post(URL, data = '{"action": "TempON"}')

        elif request.form.get('TempSensor_OFF') == 'TempSensor_OFF':
            x = requests.post(URL, data = '{"action": "TempOFF"}')

    elif request.method == 'GET':
        y = requests.get(URL)
        print("No Post Back Call")

    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug = True)
