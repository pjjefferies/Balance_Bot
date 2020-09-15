#! /usr/bin/python3

import RPi.GPIO as GPIO  # Import GPIO library

motor1in1 = 7
motor1in2 = 11
motor2in1 = 13
motor2in2 = 15
motor1enable = 25
motor2enable = ?
temp1=1
maxPWM_value = 100


GPIO.setwarnings(False)

#set GPIO numbering mode and define output pins
GPIO.setmode(GPIO.BOARD)

# Trigger with PWM
GPIO.setup(motor1enable, GPIO.OUT)  # ENA
GPIO.setup(motor1enable, GPIO.OUT)  # ENB
motor1GPIO = GPIO.PWM(25, maxPWM_value)
motor2GPIO = GPIO.PWM(YY, maxPWM_value)

# Set outputs as GPIO Output
GPIO.setup(motor1in1, GPIO.OUT)
GPIO.setup(motor1in2, GPIO.OUT)
GPIO.setup(motor2in1, GPIO.OUT)
GPIO.setup(motor2in1, GPIO.OUT)

# Set outputs low as stop to start
GPIO.output(motor1in1, GPIO.LOW)
GPIO.output(motor1in2, GPIO.LOW)
GPIO.output(motor2in1, GPIO.LOW)
GPIO.output(motor2in2, GPIO.LOW)

GPIO.setup(37,GPIO.OUT)  # Trigger - what is this for
GPIO.setup(24,GPIO.IN)      # Echo - what is this for

dc = 25   # set the speed here as a % of the full speed 
motor1GPIO.start(dc)
motor2GPIO.start(dc)

print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("(s)top (f)orward (b)ackward (r)ight (l)eft")
print("l(o)w (m)edium (h)igh (m)ax (e)xit")
print("\n")   

while(True):
    x=raw_input()
    if x=='s':
        print("stop")
        GPIO.output(motor1in1, GPIO.LOW)
        GPIO.output(motor1in2, GPIO.LOW)
        GPIO.output(motor2in1, GPIO.LOW)
        GPIO.output(motor2in2, GPIO.LOW)
        x='z'
    elif x=='f':
        print("forward")
        GPIO.output(motor1in1, GPIO.HIGH)
        GPIO.output(motor1in2, GPIO.LOW)
        GPIO.output(motor2in1, GPIO.HIGH)
        GPIO.output(motor2in2, GPIO.LOW)
        x='z'
    elif x=='b':
        print("backward")
        GPIO.output(motor1in1, GPIO.LOW)
        GPIO.output(motor1in2, GPIO.HIGH)
        GPIO.output(motor2in1, GPIO.LOW)
        GPIO.output(motor2in2, GPIO.HIGH)
        x='z'
    elif x=='r':
        print("right")
        GPIO.output(motor1in1, GPIO.LOW)
        GPIO.output(motor1in2, GPIO.HIGH)
        GPIO.output(motor2in1, GPIO.HIGH)
        GPIO.output(motor2in2, GPIO.LOW)
        x='z'
    elif x=='l':
        print("left")
        GPIO.output(motor1in1, GPIO.HIGH)
        GPIO.output(motor1in2, GPIO.LOW)
        GPIO.output(motor2in1, GPIO.LOW)
        GPIO.output(motor2in2, GPIO.HIGH)
        x='z'
    elif x=='l':
        print("low")
        p.ChangeDutyCycle(25)
        x='z'
    elif x=='m':
        print("medium")
        p.ChangeDutyCycle(50)
        x='z'
    elif x=='h':
        print("high")
        p.ChangeDutyCycle(75)
        x='z'
    elif x=='m':
        print("max")
        p.ChangeDutyCycle(100)
        x='z'
    elif x=='e':
        GPIO.cleanup()
        break
    else:
        print("<<<  wrong data  >>>")
        print("please enter the defined data to continue.....")

