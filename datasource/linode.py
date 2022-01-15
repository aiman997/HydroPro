import os
import requests
import logging
import psycopg2
import redis
import sys

cache = redis.StrictRedis(host='redis', port=6379)

# Configure Logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

def PgFetch(query, method):
    conn = psycopg2.connect("host='postgres' dbname='linode' user='postgres' password='linode123'")
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

