#!/usr/bin/python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

################################################
# GPIO | RELAY |  ADC | VR | STATE | COMPONENT #
#----------------------------------------------#
#                   RELAY 1                    #
#----------------------------------------------#
# 21   |  01   |  NA  | NA |  LOW  | MAIN PUMP #
# 22   |  02   |  NA  | NA |  LOW  | ECUP      #
# 20   |  03   |  NA  | NA |  LOW  | PHUP      #
# 16   |  04   |  NA  | NA |  LOW  | PHDWN     #
#----------------------------------------------#
#                   RELAY 2                    #
#----------------------------------------------#
# 08   |  01   | ADC0 | 01 |  LOW  | EC SENSOR #
# 07   |  02   | ADC1 | 02 |  LOW  | PH SENSOR #
# 11   |  03   | ADC2 | 03 |  LOW  | TP SENSOR #
# 05   |  04   | ADC3 | 04 |  LOW  | WL SENSOR #
# 06/25|  05   |  NA  | 05 |  LOW  | WF SENSOR #
# 12   |  06   |  NA  | 06 |  LOW  | FAN       #
# 13   |  07   |  NA  | 07 |  LOW  | SVI       #
# 19   |  08   |  NA  | 08 |  LOW  | SVO       #
#----------------------------------------------#
#                   RELAY 3                    #
#----------------------------------------------#
# 08   |  01   | ADC0 | 01 |  LOW  | LIGHT     #
# 07   |  02   | ADC1 | 02 |  LOW  | OX SENSOR #
# 11   |  03   | ADC2 | 03 |  LOW  | HD SENSOR #
# 05   |  04   | ADC3 | 04 |  LOW  |           #
################################################

actHIGHList = [12]
actLOWList = [21,22,20, 16, 8, 7, 11, 5, 6, 13, 19]

    

    
# Sleep time variables

sleepTimeShort = 0.5
sleepTimeLong = 0.1

# MAIN LOOP =====
# ===============

try:
    for i in actHIGHList:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.LOW)
    
    for i in actLOWList:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)
    #for i in gpioList:
    #GPIO.output(13,GPIO.LOW) #PI_FAN
    #GPIO.output(7 ,GPIO.HIGH)  
    #GPIO.output(11,GPIO.HIGH)   
    #GPIO.output(8 ,GPIO.HIGH)   
    #GPIO.output(5 ,GPIO.HIGH)  
    #GPIO.output(12,GPIO.HIGH)#wf 
    #GPIO.output(21,GPIO.HIGH)  
    #GPIO.output(22,GPIO.HIGH)   
    #GPIO.output(20,GPIO.HIGH)  
    #GPIO.output(16,GPIO.HIGH)  
    #GPIO.output(19,GPIO.HIGH)  
    GPIO.output(6 ,GPIO.LOW)   
    
# End program cleanly with keyboard
except KeyboardInterrupt:
    print(" Quit")

    # Reset GPIO settings
    # GPIO.setwarnings(False)
    GPIO.cleanup()


