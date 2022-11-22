import asyncio
import board
import countio
import time
import pwmio
import digitalio
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
    pwm_servo2, min_pulse=600, max_pulse=2460
)

note = input("Select string: ").upper()

output_freq = 0;
prev_time = 0
target_freq = string_notes[note]
print("Target frequency: ", target_freq, "\n")

# takes in measured frequency and target frequency, moves servo accordingly
def tune(freq, target_freq):
    if freq > target_freq:
        move_servo(1.0,0.1)
        print("Frequency too high , strum again!")
    elif freq < target_freq:
        move_servo(-1.0,0.1)
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

async def monitor_freq(pin):
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                global prev_time, output_freq
                curr_time = time.monotonic_ns()
                delta_t = curr_time - prev_time
                output_freq = interrupt.count / (delta_t / 1000000000)
                prev_time = curr_time
                interrupt.count = 0
                #print("Period is", delta_t, " ns")
                #print("Frequency is", output_freq, "Hz")
            await asyncio.sleep(0.1)

async def turn_motor():
    # Test with different output freq
    while output_freq != target_freq:
        global output_freq
        output_freq = tune(output_freq, target_freq)
        await asyncio.sleep(0)
    led.value = False


async def main():
    freq_task = asyncio.create_task(monitor_freq(board.D25))
    motor_task = asyncio.create_task(turn_motor())
    print("Starting...")
    await asyncio.gather(freq_task, motor_task)

asyncio.run(main())
