# In-Plane Thermal Conductivity Project

## Table of Contents
- [In-Plane Thermal Conductivity Project](#in-plane-thermal-conductivity-project)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Project Structure](#project-structure)
  - [Using the Repository](#using-the-repository)
    - [Installation](#installation)
    - [Running the program](#running-the-program)
    - [Exiting the program](#exiting-the-program)
  - [Database Schema](#database-schema)
  - [TC08 Note](#tc08-note)

## Description
This project integrates various components such as server, database, web application, controls, and computations for in-plane thermal conductivity analysis. It utilizes a robust Node.js server and a responsive front-end built with Next.js alongside several python scripts communicating with the hardware.

## Project Structure
- **Client**: Implements the user interface using Next.js and manages HTTP requests with axios.
- **Server**: A Node.js server employing Express.js for HTTP requests and connecting to an SQLite3 database, with database manipulation facilitated by Knex.
- **Control**: A collection of python scripts dedicated to recording the data from the thermocouples, controlling the heaters, and calculating the thermal conductivity
  - *Thermal Control*
    - Pico_Talker.py: Setting the duty cycle of the heaters based on the control mode set by the user in the website.
  - *Thermocouple*
    - writeFromDAQ.py: Recieves the data from the TC-08 DAQ and writes the temperatures to the temperature table in the database
    - graphLive.py: Plots the live temperature data along side calculated sin fit for active tests.
    - graphFull.py: Similar functionality to graphLive.py but for looking at the data of previous tests. 


## Using the Repository

### Installation

1. Update and upgrade ubuntu packages
  ```
  sudo apt update && sudo apt upgrade
  ```
2. Install picosdk and drivers for the Pico Logger TC-08. Instructions from: https://www.picotech.com/downloads/linux
  ```
  sudo bash -c 'wget -O- https://labs.picotech.com/Release.gpg.key | gpg --dearmor > /usr/share/keyrings/picotech-archive-keyring.gpg'
  sudo bash -c 'echo "deb [signed-by=/usr/share/keyrings/picotech-archive-keyring.gpg] https://labs.picotech.com/picoscope7/debian/ picoscope main" >/etc/apt/sources.list.d/picoscope7.list'
  sudo apt-get update
  sudo apt-get install libusbtc08
  ```

3. Install Python 3.11
  ```
  sudo apt install python3.11
  ```
4. Install pip
  ```
  sudo apt install python3-pip
  ```

5. Install venv pip package
  ```
  python3.11 -m pip install venv
  ```
6. Install curl
  ```
  sudo apt install curl
  ```
7. Install nvm  
  ```
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.6/install.sh | bash
  source ~/.bashrc
  ```
8. Install Node LTS 20.10.0 and specify it as default
  ```
  nvm install 20.10.0
  nvm alias default 20.10.0
  ```

9. **Clone the repository**: <!-- Replace git clone command with one specifying version once its released -->
  ```
  git clone https://github.com/jordanabinader/In_Plane_Thermal_Conductivity.git
  cd In_Plane_Thermal_Conductivity/
  ```
10. **Setup the python virtual environment**
  ```
  python3.11 -m venv iptc_venv
  ```
  
11. **Install node dependencies**:
   - For the client:
       ```
       cd client
       npm install
       cd ../
       ```
   - For the server:
       ```
       cd server
       npm install
       cd ../
       ```
12. **Install python dependencies**
  ```
  source iptc_venv/bin/activate
  python3.11 -m pip install -r requirements.txt
  ```

### Running the program
Your current working directory should be the base folder of the In_Plane_Thermal_Conductivity repository

1. Activate the virtual environment
  ```
  source iptc_venv/bin/activate
  ```
2. Check the serial port
  ```
  ls -l /dev/serial/by-id
  ```
  The raspberry pi pico likely defaults to ttyACM0, but if not change the ttyACM0 in the command below to what this command highlights

3. Start everything up
  ```
  python3.11 Startup.py --serial-port /dev/ttyACM0
  ```

### Exiting the program
1. In the terminal window running Startup.py from the command above, hit `ctrl+c`
  
   - A normal exit will look similar to below
![Image of a nominal exit of the python script](/.imgs/nominal_script_exit.jpg)
   - If you see more than 3 or 4 print statments in a row that say `{SOMETHING} not shutting down`  the heater control board should be unplugged from and the computer restarted as this means that something went wrong in the shutdown process and the heaters can cause damage if left running while powered

It is also worthwhile to check the terminal output after ending a test to ensure that the heaters get turned off the the thermocouple DAQ gets deactivated properly. The terminal output at the end of a test should look something like the image below. Similar to the what happens when the whole system gets shutdown: If you see more than 3 or 4 print statments in a row that say `{SOMETHING} not shutting down`  the heater control board should be unplugged from and the computer restarted as this means that something went wrong in the shutdown process and the heaters can cause damage if left running while powered. 
![Image of the terminal output when a test is ended properly](/.imgs/nominal_test_end.jpg)


## Database Schema
The application uses the following SQLite3 database schemas:

- **Test Settings Table** (`testSettingTableName`):
  - `controlMode`: Float
  - `frequency`: Float
  - `amplitude`: Float
  - `datetime`: DateTime

- **Power Table** (`powerTableName`):
  - `heaterNum`: Float
  - `mV`: Float
  - `mA`: Float
  - `dutyCycle`: Float
  - `datetime`: DateTime

- **Temperature Table** (`temperatureTableName`):
  - `datetime`: DateTime (Default to current time)
  - `relTime`: Float
  - `temp1` to `temp8`: Float (temperature readings for 8 different points)


## TC08 Note
For use with TC-08, you may have to modify library.py of picosdk so it can manually find the installed library

ex. "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/picosdk/library.py"

Edit the first line after def _load(self):

library_path = find_library(self.name) ->
library_path = '/Library/Frameworks/PicoSDK.framework/Libraries/libusbtc08/libusbtc08.dylib' For running on Charlie's Macbook Pro
