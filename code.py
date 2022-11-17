# SPDX-FileCopyrightText: 2021 jedgarpark for Adafruit Industries
# SPDX-License-Identifier: MIT
# Pico servo demo
# Hardware setup:
# Servo on GP0 with external 5V power supply
# Button on GP3 and ground
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import pwmio
from adafruit_motor import servo
print("Servo test")
led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT
led.value = True

# Servo setup
pwm_servo = pwmio.PWMOut(board.A2, duty_cycle=2 ** 15, frequency=50)
servo1 = servo.ContinuousServo(
    pwm_servo, min_pulse=750, max_pulse=2250
)

# takes in measured frequency and target frequency, moves servo accordingly
def tune(freq, target_freq, servo):
    if freq > target_freq:
        move_servo(1,1,servo)
    elif freq < target_freq:
        move_servo(-1,1,servo)
        
def move_servo(throttle, interval, servo):
    servo.throttle = throttle
    time.sleep = interval

while True:
    servo1.throttle = 0.1
    time.sleep(1)
    servo1.throttle = 0.0
    time.sleep(1)
    servo1.throttle = -0.1
    time.sleep(1)
    servo1.throttle = 0.0
    time.sleep(1)