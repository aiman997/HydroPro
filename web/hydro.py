from flask import Flask, redirect, url_for, request, render_template, make_response, session, flash
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
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'aiman'
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

def pgAuth(query, arg):
    try:
        conn = psycopg2.connect(database='hydrodb', user='postgres', password='eamon2hussien', host='postgres')
        # Check if account exists using MySQL
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #cursor.execute('SELECT * FROM hydro.usrs WHERE username = %s', (username,))
        cursor.execute(query, (arg,))
        #cursor.execute(query, arg)
        # Fetch one record and return result
        account = cursor.fetchone()
        return account
    except Exception as e:
        logging.warning("pgAuth" + str(e))

def pgSession(query, arg):
    try:
        conn = psycopg2.connect(database='hydrodb', user='postgres', password='eamon2hussien', host='postgres')
        # Check if account exists using MySQL
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #cursor.execute('SELECT * FROM hydro.usrs WHERE username = %s', (username,))
        cursor.execute(query, arg)
        #cursor.execute(query, arg)
        # Fetch one record and return result
        account = cursor.fetchone()
        return account
    except Exception as e:
        logging.warning("pgAuth" + str(e))
def pgInsert(fullname, username, _hashed_password, email):
    try:
        conn = psycopg2.connect(database='hydrodb', user='postgres', password='eamon2hussien', host='postgres')
        # Check if account exists using MySQL
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("INSERT INTO hydro.usrs (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
        conn.commit()
        return True
    except Exception as e:
        logging.warning("pgInsert" + str(e))

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/')
def home():
    #check if user is logged in
    if 'loggedin' in session:
        #show home page
        logging.warning("logged in")
        return render_template('home.html', username = session['username'])
    #if not loggedin show login
    logging.warning("not logged in")
    return redirect(url_for('login'))

@app.route('/login/', methods=['GET','POST'])
def login():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        logging.warning(password)
        query =  'SELECT * FROM hydro.usrs WHERE username = %s'
        arg = username
        account = pgAuth(query, arg)
        if account:
            password_rs = account['password']
            logging.warning(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect       
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect       
            flash('Incorrect username/password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
        #cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            # Create variables for easy access
            fullname = request.form['fullname']
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            _hashed_password = generate_password_hash(password)
            arg = username
            account = pgAuth(query, arg)

            #Check if account exists using MySQL
            #cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            #account = cursor.fetchone()
            #print(account)
            # If account exists show error and validation checks
            if account:
                flash('Account already exists!')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!')
            elif not re.match(r'[A-Za-z0-9]+', username):
                flash('Username must contain only characters and numbers!')
            elif not username or not password or not email:
                flash('Please fill out the form!')
            else:

                # Account doesnt exists and the form data is valid, now insert new account into users table
                if pgInsert(fullname, username, _hashed_password, email ) == True:
                    flash('You have successfully registered!')
        
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            flash('Please fill out the form!')
            # Show registration form with message (if any)
        return render_template('register.html')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))
                     
@app.route('/profile')
def profile(): 
    #cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Check if user is loggedin
    if 'loggedin' in session:
        logging.warning("seesion[id]")
        logging.warning([session['id']])
        query = 'SELECT * FROM hydro.usrs WHERE id = %s'
        arg = [session['id']]
        account = pgSession(query, arg)
        
        #cursor.execute('SELECT * FROM hydro.usrs WHERE id = %s', [session['id']])
        #account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
        # User is not loggedin redirect to login page
    return redirect(url_for('login'))



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

@app.route('/Dash')
def dash():
    return render_template('dash.html')

@app.route('/testd')
def testd():
    return render_template('pro.html')

@app.route('/pm')
def pm():
    return render_template('pm.html')

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
    
    if request.method == 'post':
        if request.form.get('ph_on') == 'ph_on':
            pubcontrols('/phon')

        elif request.form.get('ph_off') == 'ph_off':
            pubcontrols('/phoff')

        elif request.form.get('ph_read') == 'ph_read':
            pubcontrols('/phread')
            time.sleep(5)
            pubrcontrols('/phread')

        elif request.form.get('ec_on') == 'ec_on':
            pubcontrols('/econ')

        elif request.form.get('ec_off') == 'ec_off':
            pubcontrols('/ecoff')

        elif request.form.get('ec_read') == 'ec_read':
            pubcontrols('/ecread')
            pubrcontrols('/ecread')

        elif request.form.get('temp_on') == 'temp_on':
            pubcontrols('/tempon')

        elif request.form.get('temp_off') == 'temp_off':
            pubcontrols('/tempoff')

        elif request.form.get('temp_read') == 'temp_read':
            pubcontrols('/tempread')
            pubrcontrols('/tempread')

        elif request.form.get('mpump_on') == 'on':
            pubcontrols('/mpumpon')
        
        elif request.form.get('mpump_off') == 'off':
            pubcontrols('/mpumpoff')

        elif request.form.get('auto') == 'auto':
            pubautocontrol('/auto')
            
    elif request.method == 'get':
        print("no post back call")
    
    
    return render_template("index.html", PHREAD=PHREADING, PHSTATE=PHSTATE, ECREAD=ECREADING, ECSTATE=ECSTATE)


if __name__ == '__main__':
    app.run(debug = True)
