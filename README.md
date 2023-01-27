# qtune: Automatic Guitar Tuner
This is a repository for an automatic guitar tuner project. 
This project utilizes the Adafruit Feather RP2040 with CircuitPython.

## Hardware Setup
1. Connect the two servo motors using it's 3 pins. The power wire should connect to one of the 3.3V pins, the ground wire should connect to the GND pin, and the signal wire should connect to the A1 for one motor and the A2 pin for the other motor. 
2. Connect the LCD screen using the relevant pins on the RP 2040.
3. Connect the output of the vibration sensor to the comparator circuit and place the sensor flat on the surface of the guitar.
4. Connect the 3D printed tuning attachment to the motors and attach it to the tuning pegs.

## Software Installation
In order to start writing Python scripts for the RP2040, follow these steps:
1. Download the latest version of CircuitPython for the RP2040 here: https://circuitpython.org/board/adafruit_feather_rp2040/
2. Start the bootloader on the board by first plugging in the device, holding down the BOOTSEL button and then pressing the RESET button once. The board will now be mounted as an external filesystem with a name similar to RPI-RP2.
3. Copy the UF2 file onto the mounted board.
4. Connect to the REPL via USB serial port. This can be done using putty or nRF Terminal in VSCode for example.
5. Copy the repo and add the code.py file into the mounted board. The board should flash and run the code.
6. Connect to the USB serial port via the nRF terminal in VSCode or minicom if you're using a Mac.

## Usage
The board contorls the two servo motors and a LCD based on user input and the processed input frequency from the comparator circuit implementation. The comparator circuit is used to process the analog input from the vibration sensor and convert it to a digital output that can be interrpreted in software.

The LCD is connected to two button, one button switches between the type of string to be tuned and the second button confirms the string selection. Information is displayed on the LCD as the programm progresses.

## Overall Procedure
1. Press one button to iterate through all the string options and press the other button to select the current string displayed on the LCD.
2. The target frequency will then display on the LCD for a moment before the program intiates the frequency measurements/calculations.
3. As the program runs, it will first measure the frequency and compare it against the target frequency. When it's too low or too high, the LCD will notify the user and the motors will turn either left or right, which moves the tuning peg.
4. If the measured frequency is correct then the tuning is completed and the program ends. Otherwise, s tep 3. is repeated until it is reached.

