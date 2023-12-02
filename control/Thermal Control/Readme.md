# Thermal Control
This folder contains the code necessary to control the heaters connected to the In-Plane Thermal Conductivity (IPTC) Power Distribution and Control PCB that integrates with the larger Web App

## Getting Started
Instructions for how to get started using the power distribution and control PCB and heater control software
### Pico_Talker
Pico_Talker.py is the python script that controls the power output of the heaters.

#### Instructions

1. Install Python. This code was tested to run on Python 3.11.6 and Python 3.11.5
1. Install required packages with: `pip install -r requirements.txt`
1. Run the script with `python Pico_Talker.py {ARGUMENTS}` with the desired arguments. See the arguments section below. 

#### Arguments

For instructions on how to use optional arguments [see this documentation from python](https://docs.python.org/3/howto/argparse.html#introducing-optional-arguments).

Example: `python Pico_Talker.py --port COM4 --baud 115200 --database storage.db`

**--port:** Optional
- Serial Port the IPTC Power Distribution and Control PCB is connected to
- If no port is passed, it uses the Serial_Helper.terminalChooseSerialDevice() to get user input on which port to use

**--baud:** Optional. Default = 115200
- Baud rate that the IPTC Power Distribution and Control PCB is communicating at.
- Shouldn't be changed unless you have made changes to the arduino code

**--database:** Optional. Default "your_database.db"
- The relative path to the database relative to the current working directory of this python script (where the script was started from), or the absolute path on the computer

### IPTC Power Distribution and Control PCB and Arduino Code
This PCB was designed after initial assemblies on protoboards had hazards in the form of insufficient ampacity of the wires use. This PCB also greatly simplified the assembly and reduced the risk of shorts. To make your own, the suggested manufacturer is JLCPCB as that is what the design rules are for and where this project ordered from. To order the exact same thing, upload the [IPTC Power Distribution and Control Fabrication Output zip file](IPTC%20PCB/IPTC%20Power%20Distribution%20and%20Control%20Fabrication%20Output.zip) to JLCPCB. Our order specifications were as follows:
- 2 Layer Board
- 1.6mm thickness
- 1 oz outer copper weight
- HASL (with lead) 

![Image of the Assembled IPTC Power Distribution and Control PCB designed by Ben Veghte](IPTC%20Power%20Distribution%20and%20Control%20PCB.jpg)

The code, in the [IPTC_heater_control](IPTC_heater_control/) folder, can be uploaded directly to the Raspberry Pi Pico on the PCB. Although the PCB has pins broken out for SPI, intended for MAX31855KASA breakout boards, the arduino code and Pico_Talker.py in the current state does not support the use of these pins. If you wish to add this functionality, make the changes necessary and submit a pull-request to the repository. In order to make the addition as seamless as possible, follow the [Serial Communication Pattern](Serial%20Communication%20Pattern.md).

In order to upload the code to the PCB, you need to use the Arduino Mbed OS RP2040 Boards from the Boards Manager in the Arduino IDE and [install the Adafruit INA-260 library](https://learn.adafruit.com/adafruit-ina260-current-voltage-power-sensor-breakout/arduino#install-adafruit-ina260-library-3024064)


## Web Interface

Although this script has a couple endpoints, it isn't a webpage that is human readable, the endpoints are just for the primary website to send put requests to to tell Pico_Talker.py to update internal states, such as the current test settings and if the test has ended. Do not send HTTP requests to these endpoints unless you know what your are doing because it could have unintended side effects.