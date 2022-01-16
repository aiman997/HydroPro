import os
import requests
import logging
import psycopg2
import redis
import sys
import logging
import time
import logging
"""
logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')
"""

cache = redis.StrictRedis(host='redis', port=6379)

def PgFetch(query, method):
    conn = psycopg2.connect("host='postgres' dbname='hydrodb' user='postgres' password='eamon2hussien'")
    cur = conn.cursor()
    dbquery = cur.execute(query)
    if method == 'GET':
        result = cur.fetchone()
    else:
        result = ""
    conn.commit()
    cur.close()
    conn.close()
    return result


URL = 'http://192.168.101.26:80'
def fetch(jsdata):
    x = requests.post(URL, data = jsdata)

    keyvalues = x.text
    values = re.findall("\{(.*?)\}", keyvalues)

    result = []
    for row in values:
        x = row.split(',')
        for column in x:
            key_value_pairs = column.split(':')
            result += key_value_pairs
    res_dct = {result[i]: result[i + 1] for i in range(0, len(result), 2)}
    return res_dct

def main():
    while (1):
        time.sleep(60)
        localtime = time.localtime()
        logging.warning('BEFORE' + time.strftime("%I:%M:%S %p", localtime))
        cache.publish('x', time.strftime("%I:%M:%S %p", localtime))
        logging.warning('AFTER' + time.strftime("%I:%M:%S %p", localtime))
        """
        res_dct = fetch('{"action": "waterON"}')
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
        , res_dct['PHDOWN_Status'])
        PgFetch(query, "POST")
        """

if __name__ == '__main__':
    main()
