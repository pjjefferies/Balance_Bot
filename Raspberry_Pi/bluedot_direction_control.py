#! /usr/bin/python3


from bluedot import BlueDot
from time import sleep

bd = BlueDot()

bd.wait_for_connection()

def bd_drive():
    if bd.is_pressed:
        x, y = bd.position.x, bd.position.y
        return x, y
    else:
        return 0, 0


if __name__ == '__main__':
    prev_position = [101, 101]  # start with impossible position for comp.
    
    while True:
        position = list(bd_drive())
        if position != prev_position:
            print(rf'x:{position[0]}, y:{position[1]}')
        prev_position = position
        sleep(0.2)
