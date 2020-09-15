#! /usr/bin/python3


from bluedot import BlueDot
from signal import pause

bd = BlueDot()

def move(pos):
    if pos.top:
        print('Up:', str(pos.distance))
    elif pos.bottom:
        print('Down:', str(pos.distance))
    if pos.left:
        print('	Left:', str(pos.distance))
    elif pos.right:
        print('Right:', str(pos.distance))

def stop():
    print('Stop')

bd.when_pressed = move
bd.when_moved = move
bd.when_released = stop

pause()  # causes process to sleep until a signal is received
