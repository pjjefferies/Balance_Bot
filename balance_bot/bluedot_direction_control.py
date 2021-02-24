#! /usr/bin/python3

import logging
from config import cfg

from bluedot import BlueDot
from time import sleep
from balance_bot.config import cfg

logger = logging.getLogger(__name__)

bd = BlueDot()

bd.wait_for_connection()

def bd_drive():
    """
    BlueDot wrapper to send y (fwd.), x (right/left) when bluedot is touched
    or 0, 0 if it's not pressed.
    """
    if bd.is_pressed:
        x, y = -bd.position.x, -bd.position.y
        return y, x
    else:
        return 0, 0


if __name__ == '__main__':
    prev_position = [101, 101]  # start with impossible position for comp.
    
    while True:
        position = list(bd_drive())
        if position != prev_position:
            print(rf'x:{position[1]}, y:{position[0]}')
        prev_position = position
        sleep(0.2)
