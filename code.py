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
import adafruit_character_lcd.character_lcd as characterlcd

string_notes = {'E': 82, 'A': 110, 'D': 147, 'G': 196, 'B': 247, 'E': 330 }
notes = {0: 'E', 1: 'A', 2: 'D', 3: 'G', 4: 'B', 5: 'E'} 
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

# takes in measured frequency and target frequency, moves servo accordingly
def tune(freq, target_freq):
    if freq > target_freq:
        move_servo(1,0.1)
        freq -= 5 # measure freq here
        lcd.clear()
        print("Frequency too high , strum again!")
        lcd.message = str(freq) + " too high,\nstrum again!"
    elif freq < target_freq:
        move_servo(-1,0.1)
        freq += 5 # measure freq here
        lcd.clear()
        print("Frequency too low, strum again!")
        lcd.message = str(freq) + " too low,\nstrum again!"
    print("Tuning...\n input_freq=",freq)
    return freq
        
def move_servo(throttle, interval):
    servo1.throttle = throttle
    time.sleep(interval)
    servo2.throttle = throttle
    time.sleep(interval)
    servo1.throttle = 0
    time.sleep(interval)
    servo2.throttle = 0
    time.sleep(interval)

lcd.message = "Select string"
# note = input("Select string: ").upper()
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
        print(note)
    lcd.message = "Select string "+note
print("Done selecting string")
lcd.clear()
lcd.message = "Selected string \n" + note.upper()
time.sleep(0.5)

led.value = True
output_freq = 50
target_freq = string_notes[note]
print("Target frequency: ", target_freq, "\n")
lcd.clear()
lcd.message = "Target: " + str(target_freq)

# Test with test output frequency
while output_freq != target_freq:
    output_freq = tune(output_freq, target_freq)
lcd.clear()
lcd.message = "Finished\ntunning!"
led.value = False