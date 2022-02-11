#!/usr/bin/env python
import sys
sys.path.append('../')
import time
from flask import Flask
from flask import json, request, render_template, redirect, url_for
from adafruit_ads1x15.analog_in import AnalogIn
import time
import board
import busio
import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS
from DFRobot_ADS1115 import ADS1115
from DFRobot_EC      import DFRobot_EC
from DFRobot_PH      import DFRobot_PH

ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16

ads1115 = ADS1115()
ec      = DFRobot_EC()
ph      = DFRobot_PH()
ec.begin()
ph.begin()

PH_State     = False
PH_Reading   = 0.0
EC_State     = False
EC_Reading   = 0.0
TEMP_State   = False
TEMP_Reading = 0.0
WL_State     = False
WL_Reading   = 0.0
MPUMP_State   = False
ECUP_State   = False
PHUP_State   = False
PHDWN_State  = False


app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
#CH1 26
#CH2 19
#CH3 13
#CH4 6
#CH5 21
#CH6 20
#CH7 16
#CH8 12

gpioList = [26, 19, 13, 6, 12, 16, 20, 21]
pinmap = {"PH": 26, "EC": 19, "TEMP":13, "WL":6, "ECUP":21, "PHUP":20, "PHDWN":16, "MPUMP":12} 
sleepTimeShort = 0.2
sleepTimeLong = 0.1
for i in gpioList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.LOW)

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

@app.route('/PHon', methods=['GET'])
def PHon(): #PH(bool PHstate) 1 or 0
    try:
        GPIO.output(pinmap['PH'], GPIO.HIGH)
        global PH_State
        PH_State = True
        data = {"PH_State": PH_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
        return str

@app.route('/PHoff', methods=['GET'])
def PHoff():
    try:
        GPIO.output(pinmap['PH'], GPIO.LOW)
        global PH_State
        PH_State = False
        data = {"PH_State": PH_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/PHread', methods=['GET'])
def PHread():
        GPIO.output(pinmap['PH'], GPIO.HIGH)
        global PH_Reading
        global PH_State
        PH_State = True

        try:
            #Read your temperature sensor to execute temperature compensation
            temperature = 25 #change to generate real value
            #Set the IIC address
            ads1115.setAddr_ADS1115(0x48)
            #Sets the gain and input voltage range.
            ads1115.setGain(ADS1115_REG_CONFIG_PGA_4_096V)
            #Get the Digital Value of Analog of selected channel
            adc0 = ads1115.readVoltage(0)
            #Convert voltage to EC with temperature compensation
            PH_Reading = ph.readPH(adc0['r'],temperature)
            PHV = adc0['r']
            #print ("Temperature:%.1f ^C EC:%.2f us/cm PH:%.2f " %(temperature,EC,PH))
            print ("Temperature:%.1f ^C PHmV:%.2f mv PH:%.2f" %(temperature,PHV,PH_Reading))
            #time.sleep(1.0)
            GPIO.output(pinmap['PH'], GPIO.LOW)
            PH_State = False
            data = {"PH_Reading": PH_Reading,"PH_State": PH_State}
            response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
            print(response)
            return response

        except Exception as e:
            str = f'Error: {str(e)}'
        return str

@app.route('/ECon', methods=['GET'])
def ECon():
    GPIO.output(pinmap['EC'], GPIO.HIGH)
    global EC_State
    EC_State = True
    try:
        data = {"EC_State": EC_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response
    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/ECoff', methods=['GET'])
def ECoff():
    GPIO.output(pinmap['EC'], GPIO.LOW)
    global EC_State
    try:
        GPIO.output(pinmap['EC'], GPIO.LOW)
        global EC_State
        EC_State = False
        data = {"EC_State": EC_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        er = f'Error: {str(e)}'
    return er

@app.route('/ECread', methods=['GET'])
def ECread():
    GPIO.output(pinmap['EC'], GPIO.HIGH)
    global EC_Reading
    global EC_State
    EC_State = True
    try:
        #Read your temperature sensor to execute temperature compensation
        temperature = 25
        #Set the IIC address
        ads1115.setAddr_ADS1115(0x48)
        #Sets the gain and input voltage range.
        ads1115.setGain(ADS1115_REG_CONFIG_PGA_4_096V)
        #Get the Digital Value of Analog of selected channel
        adc1 = ads1115.readVoltage(1)
        #Convert voltage to EC with temperature compensation
        EC_Reading = ec.readEC(adc1['r'],temperature)
        ECV = adc1['r']
        #PH_Reading = ph.readPH(adc1['r'],temperature)
        #print ("Temperature:%.1f ^C EC:%.2f us/cm PH:%.2f " %(temperature,EC,PH))
        print ("Temperature:%.1f ^C ECmV:%.2f mv EC:%.2f us/cm PH:%.2f" %(temperature,ECV,EC_Reading,PH_Reading))
        #time.sleep(1.0)
        GPIO.output(pinmap['EC'], GPIO.LOW)
        PH_State = False

        data = {"EC_Reading": EC_Reading, "EC_State": EC_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        er = f'Error: {str(e)}'
    return er

@app.route('/TEMPon', methods=['GET'])
def TEMPon():
    try:
        GPIO.output(pinmap['TEMP'], GPIO.HIGH)
        global TEMP_State
        TEMP_State = True
        data = {"TEMP_State": TEMP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/TEMPoff', methods=['GET'])
def TEMPoff():
    try:
        GPIO.output(pinmap['TEMP'], GPIO.LOW)
        global TEMP_State
        TEMP_State = False
        data = {"TEMP_State": TEMP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/TEMPRead', methods=['GET'])
def TEMPRead():
    try:
        GPIO.output(pinmap['TEMP'], GPIO.HIGH)
        global TEMP_Reading
        TEMP_Reading = float(AnalogIn(ads, ADS.P0).voltage)
        data = {"TEMP_Reading": TEMP_Reading}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/WLon', methods=['GET'])
def WLon():
    try:
        GPIO.output(pinmap['WL'], GPIO.HIGH)
        global WL_State
        WL_State = True
        data = {"WL_State": WL_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/WLoff', methods=['GET'])
def WLoff():
    try:
        GPIO.output(pinmap['WL'], GPIO.LOW)
        global WL_State
        WL_State = False
        data = {"WL_State": WL_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/WLRead', methods=['GET'])
def WLRead():
    try:
        GPIO.output(pinmap['WL'], GPIO.HIGH)
        global WL_Reading
        TEMP_Reading = float(AnalogIn(ads, ADS.P0).voltage)
        data = {"WL_Reading": WL_Reading}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/ECUPon', methods=['GET'])
def ECUPon():
    try:
        GPIO.output(pinmap['ECUP'], GPIO.HIGH)
        global ECUP_State
        ECUP_State = True
        data = {"ECUP_State": ECUP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/ECUPoff', methods=['GET'])
def ECUPoff():
    try:
        GPIO.output(pinmap['ECUP'], GPIO.LOW)
        global ECUP_State
        ECUP_State = False
        data = {"ECUP_State": ECUP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/PHUPon', methods=['GET'])
def PHUPon():
    try:
        GPIO.output(pinmap['PHUP'], GPIO.HIGH)
        global PHUP_State
        PHUP_State = True
        data = {"PHUP_State": PHUP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/PHUPoff', methods=['GET'])
def PHUPoff():
    try:
        GPIO.output(pinmap['PHUP'], GPIO.LOW)
        global PHUP_State
        PHUP_State = False
        data = {"PHUP_State": PHUP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/PHDWNon', methods=['GET'])
def PHDWNon():
    try:
        GPIO.output(pinmap['PHDWN'], GPIO.HIGH)
        global PHDWN_State
        PHDWN_State = True
        data = {"PHDWN_State": PHDWN_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/PHDWNoff', methods=['GET'])
def PHDWNoff():
    try:
        GPIO.output(pinmap['PHDWN'], GPIO.LOW)
        global PHDWN_State
        PHDWN_State = False
        data = {"PHDWN_State": PHDWN_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str
@app.route('/MPUMPon', methods=['GET'])
def MPUMPon():
    try:
        GPIO.output(pinmap['MPUMP'], GPIO.HIGH)
        global MPUMP_State
        MPUMP_State = True
        data = {"MPUMP_State": MPUMP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/MPUMPoff', methods=['GET'])
def MPUMPoff():
    GPIO.output(pinmap['MPUMP'], GPIO.LOW)
    global MPUMP_State
    MPUMP_State = False
    try:
        data = {"MPUMP_State": MPUMP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        a = f'Error: {str(e)}'
    return a
@app.route('/Tick', methods=['GET'])
def Tick():
    try:
        global PH_Reading 
        #PH_Reading = float( AnalogIn(ads, ADS.P0).voltage)
        data = {"PH_State":PH_State,"PH_Reading":PH_Reading,"EC_State":EC_State,"EC_Reading":EC_Reading,"TEMP_State":TEMP_State,"TEMP_Reading":TEMP_Reading,"WL_State":WL_State,"WL_Reading":WL_Reading,"MPUMP_State":MPUMP_State,"ECUP_State":ECUP_State,"PHUP_State":PHUP_State,"PHDWN_State":PHDWN_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        return f'Error: {str(e)}'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
