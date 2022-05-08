import time
import sys

class Sensor():
    
    def __init__(self, name, measurment, state, gpio, modelNum):
        
        self.name = name
        self.measurment = measurment
        self.state = state
        self.gpio = gpio
        self.modelNum = modelNum

    @properties
    def name(self):
        return self.name
    
    @name.setter
    def name(self,newnname):

        return self.name = newname
    
    @name.deleter
    def name(self):
        del self.name

    @properties
    def measurment(self):
        return measurment

    


  # class EC(Sensor):
       
   # def __init__(self, name, measurment, state, gpio, modelNum):
    #    super().__init__(self, name, measurment, state, gpio, modelNum)
    
     





