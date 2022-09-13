import sys
import os
import time
sys.path.append('/home/eampi/Projects/HydroPro/FlaskAPI/src/Components/base')
from Sensor import Sensor

acidVoltage = 3225.0
neutralVoltage = 2722.0
temperature = 26.0
#phValue = ''
class PH():
    #def __init__(self, name, measurment, state, gpio, modelNum):
     #   super().__init__( measurment, state)

    def readPH(self, voltage, temperature):
        global acidVoltage
        global neutralVoltage
        slope = (7.0 - 4.0) / ((neutralVoltage - 2722.0) / 3.0 - (acidVoltage - 2722.0) / 3.0)
        intercept = 7.0 - slope * (neutralVoltage - 2722.0) / 3.0
        phValue = slope * (voltage - 2722.0) / 3.0 + intercept
        round(phValue, 2)
        return str(phValue)
