import board
import countio
import time
import pulseio
import pwmio
import digitalio
from adafruit_motor import servo
import adafruit_character_lcd.character_lcd as characterlcd

try:
  import ulab.numpy as np
except ImportError:
  import numpy as np

###################### FUNCTIONS ######################

# Initialize Tuning
def init(lcd, button1, button2, start_threshold, stop_threshold):
    # Initialize Note Variables
    string_notes = {'e': 82.41, 'A': 110.00, 'D': 146.83, 'G': 196.00, 'B': 246.94, 'E': 329.63 }
    notes = {0: 'e', 1: 'A', 2: 'D', 3: 'G', 4: 'B', 5: 'E'}
    curr_note = 'e'
    notes_to_servo = {'e': 0, 'A': 1, 'D': 2, 'G': 3, 'B': 4, 'E': 5} # for moving servos
    curr_servo = 0
    
    # RESET #
    time.sleep(0.5)
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
        lcd.message = "Select String\nCurrent: \'" + note + "\'"

    # INITIALIZE VARIABLES #
    # Update the Target Frequency and Set Current Servo
    curr_note = note
    target_freq = string_notes[note]
    curr_servo = notes_to_servo[note]

    # Calculate Limits of Target Frequency and Pass Band Filter
    target_freq_low = target_freq - stop_threshold
    target_freq_high = target_freq + stop_threshold
    double_target_freq_low = target_freq*2 - stop_threshold
    double_target_freq_high = target_freq*2 + stop_threshold
    target_limits = [target_freq_low, target_freq_high, double_target_freq_low, double_target_freq_high]
    pass_band_low = target_freq - start_threshold
    pass_band_high = target_freq + start_threshold
    double_pass_band_low = target_freq*2 - start_threshold
    double_pass_band_high = target_freq*2 + start_threshold
    pass_band_limits = [pass_band_low, pass_band_high, double_pass_band_low, double_pass_band_high]
    
    return curr_note, curr_servo, target_limits, pass_band_limits

# Tune Current String with Motor
def tune(freq, turned_servo, pass_band_low, pass_band_high, target_freq_low, target_freq_high):
    # Check if Frequency is in Target Frequency Limits
    percent_tuned = -1
    if (freq > target_freq_low) and (freq < target_freq_high):
        return True, None

    throttle = 0.5
    # If Frequency is Greater than Target Frequency
    if freq > target_freq_high:
        percent_tuned = map_to(freq, pass_band_high, target_freq_high, 0, 100)

    # If Frequency is Less than Target Frequency
    elif freq < target_freq_low:
        percent_tuned = map_to(freq, pass_band_low, target_freq_low, 0, 100)
        throttle = throttle*-1
    interval = map_to(percent_tuned, 100, 0, 0.05, 1.0)
    
    # Tune Guitar by Moving Servos
    turned_servo.throttle = throttle
    time.sleep(interval)
    turned_servo.throttle = 0

    # Inform User of Progress to In Tune
    tune_bar = '['
    prog = int(map_to(percent_tuned, 0, 100, 0, 13))
    for x in range(prog):
        tune_bar += '*'
    while len(tune_bar) != 15:
        tune_bar += ' '
    tune_bar += ']'    
    return False, tune_bar

# Calculate Frequency of Input Waveform
def read_freq(rx, pulse_length, button2):
    # Reset pulseio pin
    rx.clear()
    rx.resume()
    
    while True:

        # Check if Restart Button was Pressed
        if not button2.value:
            return -1

        # Wait for Pulses to be Read
        if len(rx) == pulse_length:
            rx.pause()
            sum = 0
            val = 0

            # Sum all Pulse Times
            for i in range(0, pulse_length, 2):
                # Exclude Pulse Times Greater than Expected
                if rx[i] < 10000 and rx[i+1] < 10000:
                    sum += rx[i] + rx[i+1]
                else:
                    val = val + 2

            # Convert to Frequency with Average Pulse Time
            freq = 1 / ((sum / ((pulse_length - val)/2)) / 1000000)
            #print(freq)
            return freq

# Helper function to map value from one range to another
def map_to(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Main
def main():
    ####################### SERVO CONFIGURATION ########################
    servo1 = servo.ContinuousServo(pwmio.PWMOut(board.D13, frequency=50))
    servo2 = servo.ContinuousServo(pwmio.PWMOut(board.SCL, frequency=50))
    servo3 = servo.ContinuousServo(pwmio.PWMOut(board.SDA, frequency=50))
    servo4 = servo.ContinuousServo(pwmio.PWMOut(board.D25, frequency=50))
    servo5 = servo.ContinuousServo(pwmio.PWMOut(board.D24, frequency=50))
    servo6 = servo.ContinuousServo(pwmio.PWMOut(board.A2, frequency=50))
    servos = [servo1, servo2, servo3, servo4, servo5, servo6]

    ######################## LCD CONFIGURATION #########################
    lcd_rs = digitalio.DigitalInOut(board.D5)
    lcd_en = digitalio.DigitalInOut(board.D6)
    lcd_d7 = digitalio.DigitalInOut(board.D12)
    lcd_d6 = digitalio.DigitalInOut(board.D11)
    lcd_d5 = digitalio.DigitalInOut(board.D10)
    lcd_d4 = digitalio.DigitalInOut(board.D9)
    lcd_backlight = digitalio.DigitalInOut(board.D4)
    lcd_columns = 16
    lcd_rows = 2
    lcd = characterlcd.Character_LCD_Mono( # Initialize the lcd class
        lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
        lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

    ###################### BUTTON CONFIGURATION ########################
    button1 = digitalio.DigitalInOut(board.A1) # Change String
    button1.direction = digitalio.Direction.INPUT
    button1.pull = digitalio.Pull.UP

    button2 = digitalio.DigitalInOut(board.A0) # Select String
    button2.direction = digitalio.Direction.INPUT
    button2.pull = digitalio.Pull.UP

    ############## FOR TESTING PURPOSES (DETUNE GUITAR) ################
    throttle = 0.5
    interval = 0.5
    for i in range(1, 7):
        #move_servo(throttle, interval, i)
        throttle = throttle*-1
    ####################################################################
    
    ######################### START OF PROGRAM #########################
    # Welcome User to QTune
    lcd.clear()
    lcd.message = "Welcome to QTune"
    time.sleep(2)

    while True:
        # User Selects a String
        start_threshold = 15 # Range of Frequencies Considered
        stop_threshold = 0.5 # Range of Frequencies Considered In Tune
        curr_note, curr_servo, target_limits, pass_band_limits = init(lcd, button1, button2, start_threshold, stop_threshold)
        
        # Target Frequency (Lower/Upper Limit of "In Tune" Frequencies for a Note)
        target_freq_low = target_limits[0]
        target_freq_high = target_limits[1]
        double_target_freq_low = target_limits[2]
        double_target_freq_high = target_limits[3]
        # Pass Band Filter (Lower/Upper Limit of Frequencies for Filter)
        pass_band_low = pass_band_limits[0]
        pass_band_high = pass_band_limits[1]
        double_pass_band_low = pass_band_limits[2]
        double_pass_band_high = pass_band_limits[3]

        # Initialize Tuning Process and Inform User to Strum
        sampling_sizes = {'e': 5, 'A': 5, 'D': 5, 'G': 5, 'B': 5, 'E': 5}
        pulse_lengths = {'e': 100, 'A': 100, 'D': 140, 'G': 150, 'B': 300, 'E': 300}
        pulse_length = pulse_lengths[curr_note]
        sampling_size = sampling_sizes[curr_note]
        rx = pulseio.PulseIn(board.RX, pulse_length, False)
        rx.pause()
        in_tune = False
        restart = False
        
        while not in_tune:
            lcd.clear()
            lcd.message = "Strum the \'" + curr_note + "\'\nSamples: 0"
            time.sleep(0.5)
            # Begin Reading Frequencies
            frequencies = []
            double_frequencies = []

            while len(frequencies) < sampling_size and len(double_frequencies) < sampling_size:
                # Calculate Frequency
                curr_freq = read_freq(rx, pulse_length, button2)
                
                # Check if Restart Button was Pressed
                if curr_freq == -1:
                    restart = True
                    break

                # If current frequency is in acceptable range
                if curr_freq >= pass_band_low and curr_freq <= pass_band_high:
                    print(curr_freq)
                    frequencies.append(curr_freq)

                # Check doubled frequency range
                elif curr_freq >= double_pass_band_low and curr_freq <= double_pass_band_high:
                    print(curr_freq, "(Doubled)")
                    double_frequencies.append(curr_freq/2)
                
                # Inform User of Samples Taken
                if len(frequencies) > len(double_frequencies):
                    lcd.message = "\nSamples: " + str(len(frequencies))
                else:
                    lcd.message = "\nSamples: " + str(len(double_frequencies))

            if restart == True:
                break

            # Determine List to Use
            curr_freqs = []
            if len(double_frequencies) == sampling_size:
                curr_freqs = double_frequencies
            else:
                curr_freqs = frequencies
            curr_freqs.sort()
            print(curr_freqs)
            used_freqs = curr_freqs

            # If Range is Too Big Remove Outliers with IQR
            difference = curr_freqs[-1] - curr_freqs[0]
            if difference > stop_threshold:
                curr_freqs = np.array(curr_freqs) # Convert to Numpy array
                Q1 = np.median(curr_freqs[:int(sampling_size/2)])
                Q3 = np.median(curr_freqs[int(sampling_size/2):])
                curr_freqs = [x for x in curr_freqs if (x >= Q1 and x <= Q3)]
                
                # If Range too Big, Remove First Element
                difference = curr_freqs[-1] - curr_freqs[0]
                if (difference > stop_threshold):
                    curr_freqs.pop(0)
                    print(curr_freqs)
                    
                    # If Range Still too Big, Inaccurate Reading
                    difference = curr_freqs[-1] - curr_freqs[0]
                    if (difference > stop_threshold):
                        lcd.clear()
                        print("Invalid Reading")
                        lcd.message = "Invalid read\ntry again!"
                        time.sleep(1)
                        continue

                used_freqs = curr_freqs

            # Calculate Average Frequency
            average_freq = sum(used_freqs) / len(used_freqs)
            print("Average Frequency is " + str(average_freq) + " Hz")

            # Turn Motor to Tune or Finish Tuning
            print("TUNING\n")
            turned_servo = servos[curr_servo]
            in_tune, tune_bar = tune(average_freq, turned_servo, pass_band_low, pass_band_high, target_freq_low, target_freq_high)
            if in_tune:
                lcd.clear() # Inform User
                lcd.message = "100% in tune\n[**************]"
                time.sleep(2)
            else:
                lcd.clear()
                lcd.message = "Strum Again!\n" + tune_bar
                time.sleep(0.1)

        rx.deinit()

if __name__ == "__main__":
    main()
