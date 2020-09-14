#!/usr/bin/env python3


from bluedot import BlueDot
from time import sleep

bd = BlueDot()

bd.wait_for_connection()

def drive():
    if bd.is_pressed:
        x, y = bd.position.x, bd.position.y
        return x, y
    else:
        return 0, 0

prev_position = [101, 101]
while True:
    position = list(drive())
    if position != prev_position:
        print(rf'x:{position[0]}, y:{position[1]}')
    prev_position = position
    sleep(0.2)
