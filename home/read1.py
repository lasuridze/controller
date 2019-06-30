from OPi.constants import *
import OPi.GPIO as GPIO
 
_DATA0PIN = 3
_DATA1PIN = 5
 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(_DATA0PIN , GPIO.IN, pull_up_down=PUD_UP)
GPIO.setup(_DATA1PIN , GPIO.IN, pull_up_down=PUD_UP)
 
cardnumber = 0
bit_count = 0
for x in range(0, 26):
        data0 = GPIO.input(_DATA0PIN )
        data1 = GPIO.input(_DATA1PIN )
        while ( (data0 == 1) and (data1 == 1) ):
                data0 = GPIO.input(_DATA0PIN )
                data1 = GPIO.input(_DATA1PIN )
        cardnumber = cardnumber << 1
        if data1 == 1:
                cardnumber = cardnumber | 0x01
        bit_count = bit_count + 1
        while ( (data0 == 0) or (data1 == 0) ):
                print data0, data1
                data0 = GPIO.input(_DATA0PIN )
                data1 = GPIO.input(_DATA1PIN )
 
cardnumber = cardnumber >> 1
cardnumber = cardnumber &  0x00ffffff
print cardnumber
