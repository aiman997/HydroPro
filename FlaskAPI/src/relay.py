#!/usr/bin/python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# GPIO | Relay | State | COMP 
#----------------------------
# 21   |  01   |       | MAIN PUMP 
# 20   |  02   | LOW   | PUMP 1
# 26   |  03   |       | PUMP 2
# 16   |  04   | LOW   | PUMP 4
# 08   |  05   |       | WL SENSOR 
# 11   |  06   |       | EC SENSOiR
# 07   |  07   |       | PH SENSOR
# 05   |  08   |       | WATERFLOW SENSOR
# 06   |  09   |       | PUMP 3
# 12   |  10   | LOW   | TEMP SENSOR
# 13   |  11   |       | SOLENOID IN
# 19   |  12   |       | SOLENOID OUT


# initiate list with pin gpio pin numbers

actHIGHList = [12, 16, 8, 11, 7, 5, 6, 13, 19]
actLOWList = [21,20,26]

for i in actHIGHList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)
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
    GPIO.output(21, GPIO.HIGH)#MPUMP
    GPIO.output(20, GPIO.HIGH) #WL
    GPIO.output(26,GPIO.HIGH)  #EC
        #time.sleep(sleepTimeShort)
    GPIO.output(16, GPIO.HIGH)  #TEMP
    
   # GPIO.output(8, GPIO.LOW) #PHUP
   # GPIO.output(11, GPIO.LOW) #PHDWN
   # GPIO.output(7, GPIO.LOW) #ECUP
    #GPIO.output(21,GPIO.HIGH)
    
# End program cleanly with keyboard
except KeyboardInterrupt:
    print(" Quit")

    # Reset GPIO settings
    # GPIO.setwarnings(False)
    GPIO.cleanup()


