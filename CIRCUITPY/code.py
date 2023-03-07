import board
import countio
import time
import pwmio
import digitalio
from adafruit_motor import servo
import adafruit_character_lcd.character_lcd as characterlcd

try:
  import ulab.numpy as np
except ImportError:
  import numpy as np

string_notes = {'e': 82, 'A': 110, 'D': 147, 'G': 196, 'B': 247, 'E': 330 }
notes = {0: 'e', 1: 'A', 2: 'D', 3: 'G', 4: 'B', 5: 'E'}
notes_to_servo = {'e': 1, 'A': 2, 'D': 3, 'G': 4, 'B': 5, 'E': 6} # for moving servos
current_servo = 0
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
# pwm_servo1 = pwmio.PWMOut(board.A1, duty_cycle=2 ** 15, frequency=50)
# servo1 = servo.ContinuousServo(
#     pwm_servo1, min_pulse=500, max_pulse=2360
# )
# pwm_servo2 = pwmio.PWMOut(board.A2, duty_cycle=2 ** 15, frequency=50)
# servo2 = servo.ContinuousServo(
#     pwm_servo2, min_pulse=600, max_pulse=2460
# )
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
    global current_servo
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
        lcd.message = "Select string " + note

    # INITIALIZE VARIABLES #
    # Inform User of Selected String
    lcd.clear()
    lcd.message = "Selected string \n" + note.upper()
    time.sleep(0.5)

    # Inform User of Target Frequency and set current_servo
    target_freq = string_notes[note]
    current_servo = notes_to_servo[note]
    print("Current servo = " + str(current_servo))
    lcd.clear()
    lcd.message = "Target: " + str(target_freq) + " Hz"
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


# has current_servo as parameter
def tune(freq, target_freq_low, target_freq_high, current_servo):
    # Check if Frequency is in Target Frequency Limits
    if (freq > target_freq_low) and (freq < target_freq_high):
        lcd.clear() # Inform User
        lcd.message = "Finished\ntuning!"
        print("Finished tuning")
        time.sleep(2)
        return True

    # If Frequency is Greater than Target Frequency
    elif freq > target_freq_high:
        print("tuneing servo " + str(current_servo))
        move_servo(0.5, 0.2, current_servo)
        lcd.clear()
        print("Frequency too high, strum again!")
        lcd.message = str(freq) + " too high,\nstrum again!"
    
    # If Frequency is Less than Target Frequency
    elif freq < target_freq_low:
        print("tuneing servo " + str(current_servo))
        move_servo(-0.5, 0.2, current_servo)
        lcd.clear()
        print("Frequency too low, strum again!")
        lcd.message = str(freq) + " too low,\nstrum again!"

    time.sleep(2)
    return False


# has current_servo as parameter
def move_servo(throttle, interval, current_servo):
    print("moving servo: " + str(current_servo))
    if current_servo == 1:
        servo1.throttle = throttle
        time.sleep(interval)
        servo1.throttle = 0
    elif current_servo == 2:
        servo2.throttle = throttle
        time.sleep(interval)
        servo2.throttle = 0
    elif current_servo == 3:
        servo3.throttle = throttle
        time.sleep(interval)
        servo3.throttle = 0
    elif current_servo == 4:
        servo4.throttle = throttle
        time.sleep(interval)
        servo4.throttle = 0
    elif current_servo == 5:
        servo5.throttle = throttle
        time.sleep(interval)
        servo5.throttle = 0
    elif current_servo == 6:
        servo6.throttle = throttle
        time.sleep(interval)
        servo6.throttle = 0
    time.sleep(interval)

############### ASYNCHRONOUS FUNCTIONS ###############

# Calculate Frequency of Input Waveform
def read_freq(pin):
    with countio.Counter(pin) as interrupt:
        prev_time = 0
        while True:
            freq = 0
            if interrupt.count == 1:
                prev_time = time.monotonic_ns()
                
            # Check for Interrupt
            if interrupt.count > 10:
                # Calculate Frequency
                curr_time = time.monotonic_ns()
                delta_t = curr_time - prev_time
                freq = (interrupt.count + 1) / (delta_t / 1000000000)
                
                return freq
                
# Main
def main():
    sampling_size = 20
    
    while True:
        # Step 1: User Selects a String
        print("INITIALIZATION\n")
        init()
        
        in_tune = False
        while not in_tune:
            # Step 2: Read Frequency
            print("READ FREQUENCIES\n")
            frequencies = []
            double_frequencies = []
            
            while len(frequencies) < sampling_size and len(double_frequencies) < sampling_size:
                # Calculate Frequency
                curr_freq = read_freq(board.RX)
                
                # If current frequency is in acceptable range
                if curr_freq >= pass_band_low and curr_freq <= pass_band_high:
                    print("Frequency is", curr_freq, "Hz")
                    
                    frequencies.append(curr_freq)
                # Check doubled frequencies
                elif curr_freq >= double_pass_band_low and curr_freq <= double_pass_band_high:
                    double_frequencies.append(curr_freq)
            
            # Determine which list finished first
            if double_frequencies == sampling_size:
                frequencies = double_frequencies
            
            # Step 3: Remove Outliers with IQR
            frequencies.sort()
            print(frequencies)
            frequencies = np.array(frequencies)
            Q1 = np.median(frequencies[:int(sampling_size/2)])
            Q3 = np.median(frequencies[int(sampling_size/2):])
            frequencies = [x for x in frequencies if (x >= Q1 and x <= Q3)]
            print(frequencies)
            
            # Step 3: Calculate Average Frequency
            #print("AVERAGEING FREQUENCIES\n")
            average_freq = sum(frequencies) / len(frequencies)
            
            print("Average Frequency is " + str(average_freq) + " Hz")
            
            # Step 4: Turn Motor to Tune or Finish Tuning
            print("TUNING\n")
            in_tune = tune(average_freq, target_freq_low, target_freq_high, current_servo)

main()