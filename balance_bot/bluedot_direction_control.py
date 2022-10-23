#! /usr/bin/python3

from time import sleep
import logging
from bluedot import BlueDot
from config import cfg

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
