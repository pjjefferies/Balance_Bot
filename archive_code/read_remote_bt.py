#! /usr/bin/python3

import time
from bluezero import microbit
from bluezero import central
from bluezero import tools

UART_SRV = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
UART_TX = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'



ubit = microbit.Microbit(adapter_addr='B8:27:EB:2E:74:AE',
                         device_addr='C9:43:A5:4E:AC:98',
                         accelerometer_service=False,
                         button_service=False,
                         led_service=False,
                         magnetometer_service=False,
                         pin_service=False,
                         temperature_service=False)

ubit.connect()

# ubit.connect()print('Connected... Press a button to select mode')

def read_remote():
    


ubit.subscribe_uard(read_remote)


while True:
    


"""
mode = 0while looping:
    if ubit.button_a > 0 and ubit.button_b > 0:
        mode = 3
        ubit.pixels = [0b10001, 0b01010, 0b00100, 0b01010, 0b10001]
        time.sleep(1)
    elif ubit.button_b > 0:
        mode = 2
        ubit.pixels = [0b11111, 0b00100, 0b00100, 0b00100, 0b00100]

        time.sleep(0.25)
    elif ubit.button_a > 0:
        mode = 1
        ubit.pixels = [0b11110, 0b10000, 0b11100, 0b10000, 0b10000]
        time.sleep(0.25)

    if mode == 1:
        x, y, z = ubit.accelerometer
        if z < 0:
            print('Face up')
        else:
            print('Face down')
        time.sleep(0.5)
    elif mode == 2:
        print('Temperature:', ubit.temperature)
        time.sleep(0.5)
    elif mode == 3:
        looping = False
        print('Exiting')
"""


ubit.disconnect()
