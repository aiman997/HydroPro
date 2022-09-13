import unittest
import sys

sys.path.insert(0, '/home/eampi/Projects/HydroPro/FlaskAPI/src/Components/base')
from Sensor import Sensor

class TestSensorMethods(unittest.TestCase):

    def test_init(self):
        sen = Sensor('test', 10, 'up', 12, '12121Fd', 2)
        self.assertEqual(sen.name, 'test')
        self.assertEqual(sen.measurment, 10)
    
    def test_setters(self):
        sen = Sensor('test', 10, 'up', 12, '12121Fd', 2)
        sen.setname('newname')
        sen.setmeasurment(4)
        self.assertEqual(sen.name, 'newname')
        self.assertEqual(sen.measurment, 4)

    def test_getters(self):
        sen = Sensor('test', 10, 'up', 12, '12121Fd', 2)
        sen.setname('newname')
        sen.setmeasurment(4)
        self.assertEqual(sen.getname(), 'newname')
        self.assertEqual(sen.getmeasurment(), 4)

if __name__ == '__main__':
    unittest.main()
