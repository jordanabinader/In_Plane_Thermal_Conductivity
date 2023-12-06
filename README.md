# In-Plane Thermal Conductivity Project

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
    - graphLive.py: Active when a test is in progress, shutdown when there is no live test. Plots the live temperature data along side calculated sin fit.
    - graphFull.py: Active when there is no live test, shutdown when there is a live test. Similar functionality to graphLive.py but for going back through old data. 


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
4. To end all the scripts `ctrl+c` the command above.

Any necessary terminal commands you need to do while the webserver is active, do in a different terminal window


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
