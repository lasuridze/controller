import time

from pyA20.gpio import gpio
from pyA20.gpio import port
LED = port.PA6
gpio.init()
gpio.setcfg(LED, gpio.OUTPUT)

status = 0
while True:
    gpio.output(LED, status)
    status = 1 if status == 0 else 0
    time.sleep(0.1)
