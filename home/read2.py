import os
import sys
import time
from threading import Thread

import OPi.GPIO as GPIO

D0 = 3
D1 = 5

GPIO.setmode(GPIO.BOARD)

GPIO.setup(D0, GPIO.IN)
GPIO.setup(D1, GPIO.IN)

def listen_card():
    while True:
        cardnumber = 0
        bit_count = 0
        for x in range(0, 26):
            data0 = GPIO.input(D0)
            data1 = GPIO.input(D1)
            while (data0 == 1 and data1 == 1):
                data0 = GPIO.input(D0)
                data1 = GPIO.input(D1)

            cardnumber = cardnumber << 1
            if data1 == 1:
                cardnumber = cardnumber | 0x01
            bit_count += 1

            while (data0 == 0 or data1 == 0):
                data0 = GPIO.input(D0)
                data1 = GPIO.input(D1)
        cardnumber = cardnumber >> 1
        cardnumber = cardnumber & 0x00ffffff
        print cardnumber

listen_card()
#Thread(target=listen_pin, args=(D1,)).start()
