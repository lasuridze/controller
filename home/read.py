import os
import sys
import time
from threading import Thread

from pyA20.gpio import gpio
from pyA20.gpio import port

D0 = port.PA12
D1 = port.PA11
LED = port.PA6
COM = port.PA1

DATA = {
    D0: '0',
    D1: '1'
}

gpio.init()
gpio.setcfg(D0, gpio.INPUT)
gpio.setcfg(D1, gpio.INPUT)
gpio.setcfg(LED, gpio.OUTPUT)
gpio.setcfg(COM, gpio.OUTPUT)
#gpio.pullup(D0, 0)
#gpio.pullup(D1, 0)
#gpio.pullup(D0, gpio.PULLUP)
#gpio.pullup(D1, gpio.PULLUP)


def listen_card():
    while True:
        '''cardnumber = 0
        bit_count = 0
        for x in range(0, 26):
            data0 = gpio.input(D0)
            data1 = gpio.input(D1)
            while (data0 == 1 and data1 == 1):
                if bit_count == 0:
                    time.sleep(0.00005)
                data0 = gpio.input(D0)
                data1 = gpio.input(D1)

            cardnumber = cardnumber << 1
            if data1 == 1:
                cardnumber = cardnumber | 0x01
            bit_count += 1

            while (data0 == 0 or data1 == 0):
                data0 = gpio.input(D0)
                data1 = gpio.input(D1)
        cardnumber = cardnumber >> 1
        cardnumber = cardnumber & 0x00ffffff
        print cardnumber'''
        gpio.output(COM, 0)
        time.sleep(2)
        gpio.output(COM, 1)

listen_card()
#Thread(target=listen_pin, args=(D1,)).start()
