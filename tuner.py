import asyncio
import board
import countio
import time
import pwmio
from adafruit_motor import servo

prev = 0
freq = 0

pwm = pwmio.PWMOut(board.A2, duty_cycle=2 ** 15, frequency=50)
my_servo = servo.Servo(pwm)

async def monitor_freq(pin):
    with countio.Counter(pin) as interrupt:
        while True:
            if interrupt.count > 0:
                interrupt.count = 0
                global prev, freq
                curr = time.monotonic_ns()
                delta_t = curr - prev
                freq = 1 / (delta_t / 1000000000)
                prev = curr
                print("Frequency is", freq, "Hz")
            await asyncio.sleep(0)

async def turn_motor():
    # code to turn motor will eventually be here
    await asyncio.sleep(0)


async def main():
    freq_task = asyncio.create_task(monitor_freq(board.A1))
    motor_task = asyncio.create_task(turn_motor())
    print("Starting...")
    await asyncio.gather(freq_task)
    await asyncio.gather(motor_task)

asyncio.run(main())
