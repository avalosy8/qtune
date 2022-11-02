import time
import board
from digitalio import DigitalInOut, Direction, Pull
import pwmio
from adafruit_motor import servo

print("Servo test")

# Servo setup
pwm_servo = pwmio.PWMOut(board.GP0, duty_cycle=2 ** 15, frequency=50)
servo1 = servo.ContinuousServo(
    pwm_servo, min_pulse=500, max_pulse=2200
)  # tune pulse for specific servo

# Servo test
def servo_direct_test():
    print("servo test: 90")
    servo1.angle = 90
    time.sleep(2)
    print("servo test: 0")
    servo1.angle = 0
    time.sleep(2)
    print("servo test: 90")
    servo1.angle = 90
    time.sleep(2)
    print("servo test: 180")
    servo1.angle = 180
    time.sleep(2)


# Servo smooth test
def servo_smooth_test():
    print("servo smooth test: 180 - 0, -1º steps")
    for angle in range(180, 0, -1):  # 180 - 0 degrees, -1º at a time.
        servo1.angle = angle
        time.sleep(0.01)
    time.sleep(1)
    print("servo smooth test: 0 - 180, 1º steps")
    for angle in range(0, 180, 1):  # 0 - 180 degrees, 1º at a time.
        servo1.angle = angle
        time.sleep(0.01)
    time.sleep(1)

while True:
    # testing different movements
    # servo_direct_test()
    # servo_smooth_test() 

    # moving servo left and right
    servo1.throttle = 1
    time.sleep(1)
    servo1.throttle = -1
    time.sleep(1)