#! /usr/bin/python3

import time
import RPi.GPIO as GPIO  # Import GPIO library
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
			


class Motor:
	"""
	Object for indivisual Motor control - direction, speed
	"""
	def __init__(self, line_1, line_2, enable):
		self._line_1 = line_1
		self._line_2 = line_2
		self._enable_line = enable
		self._max_PWM_value = 100

		GPIO.setup(self._line_1, GPIO.OUT)
		GPIO.setup(self._line_2, GPIO.OUT)
		GPIO.output(self._line_1, GPIO.LOW)
		GPIO.output(self._line_2, GPIO.LOW)

		GPIO.setup(self._enable_line, GPIO.OUT)
		self._enable = GPIO.PWM(self._enable_line, self._maxPWM_value)
		self._enable.start(0)

		# GPIO.setup(37,GPIO.OUT)  # Trigger - what is this for
		# GPIO.setup(24,GPIO.IN)      # Echo - what is this for

	def move(self, *, direction=1, speed=10):
		"""
		Method to move motor
		direction: 1/True/x<>0 = Forward
		direction: 0/False = Backward
		speed: 0 - MOTOR_R_ENABLE: Percent of Full Speed for Motor Voltage
		"""
		if direction:
			GPIO.output(self._line_1, GPIO.HIGH)
        	GPIO.output(self._line_2, GPIO.LOW)
        else:
        	GPIO.output(self._line_1, GPIO.LOW)
        	GPIO.output(self._line_2, GPIO.HIGH)
        speed = min(max(speed, 0), 100)
        self._enable.ChangeDutyCycle(speed)

	def stop(self):
		GPIO.output(self.line_1, GPIO.LOW)
        GPIO.output(self.line_2, GPIO.LOW)
        self._enable.ChangeDutyCycle(0)
