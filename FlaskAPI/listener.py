#!/usr/bin/env python
import sys
sys.path.append('../')#*
import time
from flask import Flask
from flask import json, request, render_template, redirect, url_for
from adafruit_ads1x15.analog_in import AnalogIn#*is this needed?
import time
import board
import busio
import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS#*is this needed
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
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

#CH1 26 PH
#CH2 19 WL
#CH3 13 EC
#CH4 6  TEMP
#CH5 12 PHUP
#CH6 20 PHDWN
#CH7 16 ECUP
#CH8 21 MPUMP

act_HIGH_List = [26, 19, 13 ,6, 21]
act_LOW_List = [12, 16, 20]
pinmap = {"PH": 26, "EC": 13, "TEMP":6, "WL":19, "ECUP":20, "PHUP":12, "PHDWN":16, "MPUMP":21} 
sleepTimeShort = 0.2
sleepTimeLong = 0.1

for i in act_HIGH_List:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.LOW)

for i in act_LOW_List:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

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
        global PH_Reading
        global PH_State
        global TEMP_Reading
        global TEMP_State

        try:
            GPIO.output(pinmap['PH'], GPIO.HIGH)
            GPIO.output(pinmap['TEMP'], GPIO.HIGH)
            TEMP_State = True
            PH_State = True
            #Set the IIC address
            ads1115.setAddr_ADS1115(0x48)
            #Sets the gain and input voltage range.
            ads1115.setGain(ADS1115_REG_CONFIG_PGA_4_096V)
            #Get the Digital Value of Analog of selected channel
            adc0 = ads1115.readVoltage(0)
            adc1 = ads1115.readVoltage(1)
            TEMPV = adc0['r']
            temperature = TEMPV
            #Convert voltage to PH with temperature compensation
            PH_Reading = ph.readPH(adc1['r'],temperature)
            PHV = adc1['r']
            print ("temperature:%.1f ^C PHmV:%.2f mv PH:%.2f" %(temperature,PHV,PH_Reading))
            print(TEMPV)
            data = {"PH_Reading": PH_Reading,"PH_State": PH_State, "temperature": TEMP_Reading, "TEMP_State": TEMP_State}
            response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
            print(response)
            return response

        except Exception as e:
            str = f'Error: {str(e)}'
        return str

@app.route('/ECon', methods=['GET'])
def ECon():
    global EC_State
    try:
        GPIO.output(pinmap['EC'], GPIO.HIGH)
        EC_State = True
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
    global EC_Reading
    global EC_State
    global TEMP_Reading
    global TEMP_State
    try:
        GPIO.output(pinmap['EC'], GPIO.HIGH)
        GPIO.output(pinmap['TEMP'], GPIO.HIGH)
        EC_State = True
        TEMP_State = True
        #Set the IIC address
        ads1115.setAddr_ADS1115(0x48)
        #Sets the gain and input voltage range.
        ads1115.setGain(ADS1115_REG_CONFIG_PGA_4_096V)
        #Get the Digital Value of Analog of selected channel
        adc0 = ads1115.readVoltage(0)
        adc2 = ads1115.readVoltage(1)
        #Read your temperature sensor to execute temperature compensation
        TEMP_Reading = adc0['r']
        temperature = TEMP_Reading
        #Convert voltage to PH with temperature compensation
        EC_Reading = ec.readEC(adc2['r'],temperature)
        ECV = adc2['r']
        print ("temperature:%.1f ^C ECmV:%.2f mv EC:%.2f" %(temperature,ECV,EC_Reading))
        print(TEMPV)
        data = {"EC_Reading": EC_Reading, "EC_State": EC_State, "TEMP_Reading":TEMP_Reading, "TEMP_State": TEMP_State}
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
    global TEMP_Reading
    global TEMP_State
    try:
        GPIO.output(pinmap['TEMP'], GPIO.HIGH)
        TEMP_State = True
        #Set the IIC address
        ads1115.setAddr_ADS1115(0x48)
        #Sets the gain and input voltage range.
        ads1115.setGain(ADS1115_REG_CONFIG_PGA_4_096V)
        #Get the Digital Value of Analog of selected channel
        adc2 = ads1115.readVoltage(2)
        TEMP_Reading = adc2['r']
        print(TEMP_Reading)
        data = {"TEMP_State": TEMP_State, "TEMP_Reading": TEMP_Reading}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        TEMP_ERROR = f'Error: {str(e)}'
    return TEMP_ERROR

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

@app.route('/ECUPtest', methods=['GET'])
def ECUPtest():
    try:
        GPIO.output(pinmap['ECUP'], GPIO.HIGH)
        global ECUP_State
        ECUP_State = True
        data = {"ECUP_State": ECUP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        time.sleep(3)
        GPIO.output(pinmap['ECUP'],GPIO.LOW)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/PHUPon', methods=['GET'])
def PHUPon():
    try:
        GPIO.output(pinmap['PHUP'], GPIO.LOW)
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
        GPIO.output(pinmap['PHUP'], GPIO.HIGH)
        global PHUP_State
        PHUP_State = False
        data = {"PHUP_State": PHUP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

@app.route('/PHUPtest', methods=['GET'])
def PHUPtest():
    try:
        GPIO.output(pinmap['PHUP'], GPIO.LOW)
        global PHUP_State
        PHUP_State = True
        data = {"PHUP_State": PHUP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        time.sleep(25)
        GPIO.output(pinmap['PHUP'], GPIO.HIGH)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str


@app.route('/PHDWNon', methods=['GET'])
def PHDWNon():
    try:
        GPIO.output(pinmap['PHDWN'], GPIO.LOW)
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

@app.route('/PHDWNtest', methods=['GET'])
def PHDWNtest():
    try:
        GPIO.output(pinmap['PHDWN'], GPIO.HIGH)
        global PHDWN_State
        PHDWN_State = True
        data = {"PHDWN_State": PHDWN_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        time.sleep(10)
        GPIO.output(pinmap['PHDWN'], GPIO.LOW)
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

@app.route('/MPUMPtest', methods=['GET'])
def MPUMPtest():
    try:
        GPIO.output(pinmap['MPUMP'], GPIO.HIGH)
        global MPUMP_State
        MPUMP_State = True
        data = {"MPUMP_State": MPUMP_State}
        response = app.response_class(response=json.dumps(data), status=200, mimetype='application/json')
        print(response)
        time.sleep(300)
        GPIO.output(pinmap['MPUMP'], GPIO.LOW)
        return response

    except Exception as e:
        str = f'Error: {str(e)}'
    return str

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
    app.run(host='0.0.0.0', port=5000)
