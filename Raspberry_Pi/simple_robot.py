#! /usr/bin/python3

import time
import rpi_motor
import bluedot_return_command


MOTOR_L_IN_1 = 7
MOTOR_L_IN_2 = 11
MOTOR_L_ENABLE = 25
MOTOR_R_IN_1 = 13
MOTOR_R_IN_2 = 15
MOTOR_R_ENABLE = ?


class Simple_Robot:
	"""
	Basic Robot Manual control for 2-Motor Simple Robot
	"""
	def __init__(self):
		GPIO.setwarnings(False)
		#set GPIO numbering mode and define output pins
		GPIO.setmode(GPIO.BOARD)

		self.motor_l = Motor(MOTOR_L_IN_1,
			  				 MOTOR_L_IN_2,
					 		 MOTOR_L_ENABLE)
		self.motor_r = Motor(MOTOR_R_IN_1,
							 MOTOR_R_IN_2,
							 MOTOR_R_IN_2)
		self.bd_ctl = bluedot_direction_control()

	def move_in_bd_dir(time_step=1):  # time_step in seconds
		start_time = time.time()
		direction = self.bd_ctl()  # [x, y] eached scaled [-1, 1]
		if direction == [0, 0]:
			self.motor_l.stop()
			self.motor_r.stop()
		else:
			
