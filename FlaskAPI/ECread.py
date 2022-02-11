import sys
import time
ADS1115_REG_CONFIG_PGA_6_144V = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V = 0x04 # 6.144V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V = 0x06 # 6.144V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V = 0x08 # 6.144V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V = 0x0A # 6.144V range = Gain 16

from DFRobot_ADS1115 import ADS1115
from DFRobot_EC      import DFRobot_EC
from DFRobot_PH      import DFRobot_PH

ads1115 = ADS1115()
ec = DFRobot_EC()
ph = DFRobot_PH()

ec.begin
ph.begin

while True:
    temperature = 25
    ads1115.setAddr_ADS1115(0x48)
    ads1115.setGain(ADS1115_REG_CONFIG_PGA_4_096V)
    adc0 = ads1115.readVoltage(0)
    EC = ph.readPH(adc0['r'],temperature)
    ECV = adc0['r']
    print("Temperature:%.1f ^C EC:%.2f us/cm ECV:%.2f mv" %(temperature,EC,ECV))
    time.sleep(1.0)
