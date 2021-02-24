#! /usr/bin/python3

from bluezero import microbit
ubit = microbit.Microbit(adapter_addr='B8:27:EB:2E:74:AE',
                         device_addr='C9:43:A5:4E:AC:98',
                         accelerometer_service=True,
                         button_service=True,
                         led_service=True,
                         magnetometer_service=False,
                         pin_service=False,
                         temperature_service=True)
my_text = 'Hello, world'

# ubit.connect()

while my_text is not '':
    ubit.text = my_text
    my_text = input('Enter message: ')

ubit.disconnect()
