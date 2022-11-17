# SPDX-FileCopyrightText: 2021 jedgarpark for Adafruit Industries
# SPDX-License-Identifier: MIT
# Pico servo demo
# Hardware setup:
# Servo on GP0 with external 5V power supply
# Button on GP3 and ground
import time
import board
import digitalio
import pwmio
from adafruit_motor import servo

string_notes = {'E': 82, 'A': 110, 'D': 147, 'G': 196, 'B': 247, 'E': 330 }

# LED setup
LED_PIN = board.D13
led = digitalio.DigitalInOut(LED_PIN)
led.switch_to_output(value=False)
led.value = True

# Servo setup
pwm_servo1 = pwmio.PWMOut(board.A1, duty_cycle=2 ** 15, frequency=50)
servo1 = servo.ContinuousServo(
    pwm_servo1, min_pulse=500, max_pulse=2360
)
pwm_servo2 = pwmio.PWMOut(board.A2, duty_cycle=2 ** 15, frequency=50)
servo2 = servo.ContinuousServo(
    pwm_servo2, min_pulse=600, max_pulse=2360
)

# takes in measured frequency and target frequency, moves servo accordingly
def tune(freq, target_freq):
    if freq > target_freq:
        move_servo(0.1,0.1)
        freq -= 5 # measure freq here
        print("Frequency too high , strum again!")
    elif freq < target_freq:
        move_servo(-0.1,0.1)
        freq += 5 # measure freq here
        print("Frequency too low, strum again!")
    print("Tuning...\n input_freq=",freq)
    return freq
        
def move_servo(throttle, interval):
    servo1.throttle = throttle
    servo2.throttle = throttle
    time.sleep(interval)
    servo1.throttle = 0
    servo2.throttle = 0
    time.sleep(interval)

note = input("Select string: ").upper()

output_freq = 600
target_freq = string_notes[note]
print("Target frequency: ", target_freq, "\n")

# Test with test output frequency
while output_freq != target_freq:
    output_freq = tune(output_freq, target_freq)
led.value = False
time.sleep(2)
output_freq = 300
led.value = True

# Test with different output freq
while output_freq != target_freq:
    output_freq = tune(output_freq, target_freq)
led.value = False