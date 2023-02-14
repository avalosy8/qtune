####################### IMPORTS #######################
import board
import countio
import time
import pwmio
import digitalio
from adafruit_motor import servo
import adafruit_character_lcd.character_lcd as characterlcd


####################### GLOBALS #######################
string_notes = {​​​​​​​'e': 82, 'A': 110, 'D': 147, 'G': 196, 'B': 247, 'E': 330 }​​​​​​​
notes = {​​​​​​​0: 'e', 1: 'A', 2: 'D', 3: 'G', 4: 'B', 5: 'E'}​​​​​​​

start_threshold = 10 # Range of Frequencies Considered
stop_threshold = 1 # Range of Frequencies Considered In Tune

# Target Frequency (Lower/Upper Limit of "In Tune" Frequencies for a Note)
target_freq_low = 0
target_freq_high = 0
double_target_freq_low = 0
double_target_freq_high = 0

# Pass Band Filter (Lower/Upper Limit of Frequencies for Filter)
pass_band_low = 0
pass_band_high = 0
double_pass_band_low = 0
double_pass_band_high = 0

output_freq = 0 # freq for motor task to process
prev_time = 0 # state variable used to calculate period of waveform


####################### SERVOS ########################
pwm_servo1 = pwmio.PWMOut(board.A1, duty_cycle=2 ** 15, frequency=50)
servo1 = servo.ContinuousServo(
    pwm_servo1, min_pulse=500, max_pulse=2360
)
pwm_servo2 = pwmio.PWMOut(board.A2, duty_cycle=2 ** 15, frequency=50)
servo2 = servo.ContinuousServo(
    pwm_servo2, min_pulse=600, max_pulse=2460
)


################## PIN CONFIGURATION ##################
lcd_rs = digitalio.DigitalInOut(board.D5)
lcd_en = digitalio.DigitalInOut(board.D6)
lcd_d7 = digitalio.DigitalInOut(board.D10)
lcd_d6 = digitalio.DigitalInOut(board.D11)
lcd_d5 = digitalio.DigitalInOut(board.D9)
lcd_d4 = digitalio.DigitalInOut(board.D12)
lcd_backlight = digitalio.DigitalInOut(board.D4)
lcd_columns = 16
lcd_rows = 2

lcd = characterlcd.Character_LCD_Mono( # Initialize the lcd class
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, 
    lcd_d7, lcd_columns, lcd_rows, lcd_backlight)


################ BUTTON CONFIGURATION #################
button1 = digitalio.DigitalInOut(board.D25) # Change String
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.UP

button2 = digitalio.DigitalInOut(board.D24) # Select String
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.UP


###################### FUNCTIONS ######################

# Initialize Tuning
def init():
    global target_freq_low, target_freq_high, pass_band_low, pass_band_high
    global double_target_freq_low, double_target_freq_high, double_pass_band_low, double_pass_band_high
    
    # RESET #
    lcd.clear()
    selected = False
    idx = 0
    note = notes[idx]

    # WAIT UNTIL USER SELECTS A STRING #
    while not selected:
        # Check if Select String button pressed
        if not button2.value:
            selected = True
        # Check if Change String button pressed
        if not button1.value:
            # Increment Index
            idx = idx + 1 if idx < 5 else 0
            
            time.sleep(0.5)  # Debounce Button
            note = notes[idx] # Update String Note
        lcd.message = "Select string " + note.upper()
    
    # INITIALIZE VARIABLES #
    # Inform User of Selected String
    lcd.clear()
    lcd.message = "Selected string \n" + note.upper()
    time.sleep(0.5)
    
    # Inform User of Target Frequency
    target_freq = string_notes[note]
    lcd.clear()
    lcd.message = "Target: " + str(target_freq)
    time.sleep(0.5)
    
    # Calculate Limits of Target Frequency and Pass Band Filter
    target_freq_low = target_freq - stop_threshold
    target_freq_high = target_freq + stop_threshold
    pass_band_low = target_freq - start_threshold
    pass_band_high = target_freq + start_threshold
    
    # Calculate Doubled Limits
    double_target_freq_low = target_freq*2 - stop_threshold
    double_target_freq_high = target_freq*2 + stop_threshold
    double_pass_band_low = target_freq*2 - start_threshold
    double_pass_band_high = target_freq*2 + start_threshold

# Tune String Based on Frequency and Target Limits
def tune(freq, target_freq_low, target_freq_high):
    # If Frequency Higher than Highest Target Frequency
    if freq > target_freq_high:
        move_servo(0.1, 1.0) # Move Servo
        lcd.clear() # Inform User
        lcd.message = str(freq) + " too high,\nstrum again!"
        
    # If Frequency Lower than Lowest Target Frequency
    elif freq < target_freq_low:
        move_servo(-0.1, 1.0) # Move Servo
        lcd.clear() # Inform User
        lcd.message = str(freq) + " too low,\nstrum again!"
    
    return freq


# Moves Servo At Specified Throttle for a Given Time
def move_servo(throttle, interval):
    servo1.throttle = throttle
    servo2.throttle = throttle
    time.sleep(interval)
    servo1.throttle = 0
    servo2.throttle = 0
    time.sleep(interval)

############### ASYNCHRONOUS FUNCTIONS ###############

# Continuously Calculate Frequency of Input Waveform
async def monitor_freq(pin):
    with countio.Counter(pin) as interrupt:
        while True:
            # Check for Interrupt
            if interrupt.count > 0:
                global prev_time, output_freq
                # Calculate Frequency
                curr_time = time.monotonic_ns()
                delta_t = curr_time - prev_time
                output_freq = interrupt.count / (delta_t / 1000000000)
                
                # Update Prev Time and Reset Interrupt
                prev_time = curr_time
                interrupt.count = 0
                print("Frequency is", output_freq, "Hz")
            await asyncio.sleep(2.0)

# Continuously Turn Motor Until Tuned
async def turn_motor():
    while True:
        global output_freq
        # Check if Output Frequency is in Pass Band Limits
        if (output_freq > pass_band_low) and (output_freq < pass_band_high):
            # Check if Output Frequency is not in Target Frequency Limits
            if (output_freq < target_freq_low) or (output_freq > target_freq_high):
                output_freq = tune(output_freq, target_freq_low, target_freq_high) # Tune String
            
            # Tuning Finished
            else:
                lcd.clear() # Inform User
                lcd.message = "Finished\ntuning!"
                time.sleep(1)
                init() # Reset Program
        
        # Check for Doubled Frequency Values
        elif (output_freq > double_pass_band_low) and (output_freq < double_pass_band_high):
            if (output_freq < double_target_freq_low) or (output_freq > double_target_freq_high):
                output_freq = tune(output_freq, double_target_freq_low, double_target_freq_high)
            
            # Tuning Finished
            else:
                lcd.clear() # Inform User
                lcd.message = "Finished\ntuning!"
                time.sleep(1)
                init() # Reset Program
        
        await asyncio.sleep(2.0)

# Main
async def main():
    init()
    freq_task = asyncio.create_task(monitor_freq(board.RX))
    motor_task = asyncio.create_task(turn_motor())
    print("Starting...")
    await asyncio.gather(freq_task, motor_task)

# Run Program
asyncio.run(main())
