import time

class Sensor():

    def __init__(self, Name, Measurment, State, GPIO, ModelNum, Period=2):

        self.name = Name
        self.measurment = Measurment
        self.state = State
        self.gpio = GPIO
        self.modelNum = ModelNum
        self.period = 2

    def getname(self):
        return str(self.name)

    def setname(self, newname):
        self.name = newname
        return str(self.name)

    def getmeasurment(self):
        return self.measurment

    def setmeasurment(self, newmeasurment):
        self.measurment = newmeasurment
        return self.measurment

    def __str__(self):
        return str(self.name)
