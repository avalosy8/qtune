# QTune: Automatic Guitar Tuner
This is a repository for an automatic guitar tuner project. 
This project utilizes the Adafruit Feather RP2040 with CircuitPython.

## Hardware Setup
1. Using the hooks and rubber bands, secure the device on the head of the guitar. Ensure that the tuning pegs are aligned within the tuning attachment that is connected to the servo motor.
2. Using the clip on attachment, clip the piezo sensor on the edge of the guitar's head.
3. Plug the USB to Type-C cable to the power bank and power it on to start the program.
4. Using the push buttons and LCD interface, follow the instructions displayed by the LCD.

## Software Installation
In order to start writing Python scripts for the RP2040, follow these steps:
1. Download the latest version of CircuitPython for the RP2040 here: https://circuitpython.org/board/adafruit_feather_rp2040/
2. Start the bootloader on the board by first plugging in the device, holding down the BOOTSEL button and then pressing the RESET button once. The board will now be mounted as an external filesystem with a name similar to RPI-RP2.
3. Copy the UF2 file onto the mounted board.
4. Connect to the REPL via USB serial port. This can be done using putty or nRF Terminal in VSCode for example.
5. Copy the repo and add the code.py file into the mounted board. The board should flash and run the code.
6. Connect to the USB serial port via the nRF terminal in VSCode or minicom if you're using a Mac.

## Usage
The board controls the servo motors and a LCD based on user input and the processed input frequency from the comparator circuit implementation. The comparator circuit is used to process the analog input from the vibration sensor and convert it to a digital output that can be interpreted in software.

The LCD is connected to two buttons, one button switches between the type of string to be tuned and the second button confirms the string selection. Information is displayed on the LCD as the program progresses.

All of the servo motors are screwed into a 3D printed case, which properly aligns the motors to each tuning peg of the guitar. This case also has two sets of hooks screwed in to allow rubber bands to securely wrap around the device and head of the guitar.

## Overall Procedure
1. Press one button to iterate through all the string options and press the other button to select the current string displayed on the LCD.
2. The selected string will then display on the LCD for a moment before the program initiates the frequency measurements and calculations.
3. As the program runs, it will first measure the frequency and compare it against the target frequency. When it's too low or too high, the LCD will notify the user and the motors will turn either left or right, moving the tuning peg. The user will also be prompted to strum the guitar string again.
4. While the program runs, the user also has the option to restart the program and select a different string to tune. The program restarts by pressing the rightmost button at any point after the program has initiated.
5. If the measured frequency is correct, then the tuning is completed and the program restarts. Otherwise, repeat step 3 until the desired frequency value is measured.

### Demo

[![Demo](https://img.youtube.com/vi/emY8-uXGGco/0.jpg)](https://www.youtube.com/watch?v=emY8-uXGGco)