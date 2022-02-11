#!/usr/bin/python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

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

gpioList = [26, 19, 13, 6, 12, 16, 20, 21]
#26 ch1
#19 ch2
#13 ch3
#6 ch4
#21 ch5
#20 ch6
#16 ch7
#12 ch8
for i in gpioList:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.LOW)

# Sleep time variables

sleepTimeShort = 0.2
sleepTimeLong = 0.1

# MAIN LOOP =====
# ===============

try:
    #while True:
    #for i in gpioList:
    GPIO.output(12, GPIO.LOW)
    GPIO.output(26, GPIO.HIGH)
    GPIO.output(19, GPIO.HIGH)
        #time.sleep(sleepTimeShort);
        #GPIO.output(i, GPIO.HIGH)
        #time.sleep(sleepTimeLong);


# End program cleanly with keyboard
except KeyboardInterrupt:
    print(" Quit")

    # Reset GPIO settings

    GPIO.cleanup()

