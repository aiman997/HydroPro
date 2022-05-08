#!/usr/bin/python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

# GPIO | Relay
#--------------
# 26     01
# 19     02
# 13     03
# 06     04
# 12     05
# 16     06
# 20     07
# 21     08

# initiate list with pin gpio pin numbers

actHIGHList = [26, 19, 13, 6, 12, 16, 20, 21]
actLOWList = [12,16,20]

for i in actHIGHList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.LOW)
for i in actLOWList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)
    
# Sleep time variables

sleepTimeShort = 0.5
sleepTimeLong = 0.1

# MAIN LOOP =====
# ===============

try:
    #for i in gpioList:
    GPIO.output(26, GPIO.HIGH)#PH
        #GPIO.output(19, GPIO.HIGH) #WL
        #GPIO.output(13,GPIO.HIGH)  #EC
        #time.sleep(sleepTimeShort)
        #GPIO.output(6, GPIO.HIGH)  #TEMP
    #GPIO.output(12, GPIO.LOW) #PHUP
        #GPIO.output(16, GPIO.HIGH) #PHDWN
        #GPIO.output(20, GPIO.HIGH) #ECUP
    #GPIO.output(21,GPIO.HIGH)
    
# End program cleanly with keyboard
except KeyboardInterrupt:
    print(" Quit")

    # Reset GPIO settings
    # GPIO.setwarnings(False)
    GPIO.cleanup()


