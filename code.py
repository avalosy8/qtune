import board
import countio
import time
import pwmio
import digitalio
import asyncio
from adafruit_motor import servo
import adafruit_character_lcd.character_lcd as characterlcd

string_notes = {'e': 82, 'A': 110, 'D': 147, 'G': 196, 'B': 247, 'E': 330 }
notes = {0: 'e', 1: 'A', 2: 'D', 3: 'G', 4: 'B', 5: 'E'}
notes_to_servo = {'e': 1, 'A': 2, 'D': 3, 'G': 4, 'B': 5, 'E': 6} # for moving servos
current_servo = 0

start_threshold = 10 # defines range of freqs that will be considered
stop_threshold = 1 # defines range of freqs that will be considered in tune
target_freq_low = 0 # lower limit for in-tune freq
target_freq_high = 0 # upper limit for in-tune freq
pass_band_low = 0 # lower limit for freqs that will be considered
pass_band_high = 0 # upper limit for freqs that will be considered
output_freq = 0 # freq for motor task to process
prev_time = 0 # state variable used to calculate period of waveform

pwm1 = pwmio.PWMOut(board.A1, frequency=50)
pwm2 = pwmio.PWMOut(board.A2, frequency=50)
pwm3 = pwmio.PWMOut(board.A0, frequency=50)
pwm4 = pwmio.PWMOut(board.D13, frequency=50)
pwm5 = pwmio.PWMOut(board.SCL, frequency=50)
pwm6 = pwmio.PWMOut(board.SDA, frequency=50)

servo1 = servo.ContinuousServo(pwm1)
servo2 = servo.ContinuousServo(pwm2)
servo3 = servo.ContinuousServo(pwm3)
servo4 = servo.ContinuousServo(pwm4)
servo5 = servo.ContinuousServo(pwm5)
servo6 = servo.ContinuousServo(pwm6)

# Pin Config:
lcd_rs = digitalio.DigitalInOut(board.D5)
lcd_en = digitalio.DigitalInOut(board.D6)
lcd_d7 = digitalio.DigitalInOut(board.D10)
lcd_d6 = digitalio.DigitalInOut(board.D11)
lcd_d5 = digitalio.DigitalInOut(board.D9)
lcd_d4 = digitalio.DigitalInOut(board.D12)
lcd_backlight = digitalio.DigitalInOut(board.D4)
lcd_columns = 16
lcd_rows = 2

# Buttons config
button1 = digitalio.DigitalInOut(board.D25)
button2 = digitalio.DigitalInOut(board.D24)
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.UP # changes string
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.UP # selects string

# Initialize the lcd class
lcd = characterlcd.Character_LCD_Mono(
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight
)

# Allows user to select a string and sets up relevant vars to begin tuning
def init():
    global target_freq_low, target_freq_high, pass_band_low, pass_band_high
    lcd.clear()
    selected = False
    idx = 0
    note = notes[idx]

    while not selected:
        if not button2.value:
            # select curr string
            selected = True
        if not button1.value:
            if idx >= 5:
                idx = 0
            else:
                idx += 1
            time.sleep(0.5)  # debounce delay
            note = notes[idx]
        lcd.message = "Select string "+note.upper()
    lcd.clear()
    lcd.message = "Selected string \n" + note.upper()
    time.sleep(0.5)
    target_freq = string_notes[note]
    current_servo = notes_to_servo[note]
    print("Current servo = " + str(current_servo))
    lcd.clear()
    lcd.message = "Target: " + str(target_freq)
    time.sleep(0.5)
    target_freq_low = target_freq - stop_threshold
    target_freq_high = target_freq + stop_threshold
    pass_band_low = target_freq - start_threshold
    pass_band_high = target_freq + start_threshold


# takes in measured frequency and target frequency, moves servo accordingly
def tune(freq, target_freq_low, target_freq_high):
    if freq > target_freq_high:
        move_servo(0.1, 1.0)
        lcd.clear()
        print("Frequency too high, strum again!")
        lcd.message = str(freq) + " too high,\nstrum again!"
    elif freq < target_freq_low:
        move_servo(-0.1, 1.0)
        lcd.clear()
        print("Frequency too low, strum again!")
        lcd.message = str(freq) + " too low,\nstrum again!"
    return freq

# has servo_num as parameter
def tune(freq, target_freq_low, target_freq_high, servo_num):
    if freq > target_freq_high:
        move_servo(0.1, 1.0, servo_num)
        lcd.clear()
        print("Frequency too high, strum again!")
        lcd.message = str(freq) + " too high,\nstrum again!"
    elif freq < target_freq_low:
        move_servo(-0.1, 1.0, servo_num)
        lcd.clear()
        print("Frequency too low, strum again!")
        lcd.message = str(freq) + " too low,\nstrum again!"
    return freq

# Moves servo at specified throttle for specified time interval
def move_servo(throttle, interval):
    print("Moving all servos")
    servo1.throttle = throttle
    servo2.throttle = throttle
    servo3.throttle = throttle
    servo4.throttle = throttle
    servo5.throttle = throttle
    servo6.throttle = throttle

    time.sleep(interval)
    servo1.throttle = 0
    servo2.throttle = 0
    servo3.throttle = 0
    servo4.throttle = 0
    servo5.throttle = 0
    servo6.throttle = 0

    time.sleep(interval)

# has servo_num as parameter
def move_servo(throttle, interval, servo_num):
    print("moving servo: " + str(servo_num))
    if servo_num == 1:
        servo1.throttle = throttle
        time.sleep(interval)
        servo1.throttle = 0
    elif servo_num == 2:
        servo2.throttle = throttle
        time.sleep(interval)
        servo2.throttle = 0
    elif servo_num == 3:
        servo3.throttle = throttle
        time.sleep(interval)
        servo3.throttle = 0
    elif servo_num == 4:
        servo4.throttle = throttle
        time.sleep(interval)
        servo4.throttle = 0
    elif servo_num == 5:
        servo5.throttle = throttle
        time.sleep(interval)
        servo5.throttle = 0
    elif servo_num == 6:
        servo6.throttle = throttle
        time.sleep(interval)
        servo6.throttle = 0
    time.sleep(interval)

# Async function that continously runs that calculates freq of inputted waveform
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
                print("Frequency is", output_freq, "Hz")
            await asyncio.sleep(2.0)


# Async function that continuously runs that turns motor
async def turn_motor():
    while True:
        global output_freq
        if (output_freq > pass_band_low) and (output_freq < pass_band_high):
            if (output_freq < target_freq_low) or (output_freq > target_freq_high):
                output_freq = tune(output_freq, target_freq_low, target_freq_high)
                #output_freq = tune(output_freq, target_freq_low, target_freq_high, current_servo) 
            else:
                lcd.clear()
                lcd.message = "Finished\ntuning!"
                time.sleep(1)
                init();
        await asyncio.sleep(2.0)

async def main():
    init()
    freq_task = asyncio.create_task(monitor_freq(board.RX))
    motor_task = asyncio.create_task(turn_motor())
    print("Starting...")
    # move_servo(1,1,1) 
    # move_servo(1,1,2)
    # move_servo(1,1,3)
    # move_servo(1,1,4)
    # move_servo(1,1,5)
    # move_servo(1,1,6)

    await asyncio.gather(freq_task, motor_task)

asyncio.run(main())
