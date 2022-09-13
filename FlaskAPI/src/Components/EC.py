import sys
import os
import time
sys.path.append('/home/eampi/Projects/HydroPro/FlaskAPI/src/Components/base')
from Sensor import Sensor

temperature = 26.0

class EC():
    #def __init__(self, name, measurment, state, gpio, modelNum):
    #    super().__init__(name, measurment, state, gpio, modelNum)
        #self.handler = # lib 
    
    #def begin(self):

    def readEC(self, voltage, temperature):
        rawEC = voltage / 3.61276185
        value = rawEC * 2.60869565
        value = value / (1.0+0.02*(temperature-25.0))
        print(value)
        return str(value)
    
