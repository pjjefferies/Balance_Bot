#! /usr/bin/python3

import RPi.GPIO as GPIO  # Import GPIO library


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
