# qtune: Automatic Guitar Tuner
This is a repository for an automatic guitar tuner project. 
This project utilizes the Adafruit Feather RP2040 with CircuitPython.

## Hardware Setup
Connect a servo motor using it's 3 pins. The power wire should connect to one of the 3.3V pins, the ground wire should connect to the GND pin, and the signal wire should connect to the A2 pin.

## Software Installation
In order to start writing Python scripts for the RP2040, follow these steps:
1. Download the latest version of CircuitPython for the RP2040 here: https://circuitpython.org/board/adafruit_feather_rp2040/
2. Start the bootloader on the board by first plugging in the device, holding down the BOOTSEL button and then pressing the RESET button once. The board will now be mounted as an external filesystem with a name similar to RPI-RP2.
3. Copy the UF2 file onto the mounted board.
4. Connect to the REPL via USB serial port. This can be done using putty or nRF Terminal in VSCode for example.
5. Copy the repo and add the code.py file into the mounted board. The board should flash and run the code.

## Usage
The board interfaces with a single servo motor. 
Separately, we have code for interfacing with a comparator circuit that takes in simple sine wave and converts it into a square wave.
