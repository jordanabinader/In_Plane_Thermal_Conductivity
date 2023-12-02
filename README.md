# In-Plane Thermal Conductivity Project

## Description
This project integrates various components such as server, database, web application, controls, and computations for in-plane thermal conductivity analysis. It utilizes a robust Node.js server and a responsive front-end built with Next.js alongside several python scripts communicating with the hardware.

## Project Structure
- **Client**: Implements the user interface using Next.js and manages HTTP requests with axios.
- **Server**: A Node.js server employing Express.js for HTTP requests and connecting to an SQLite3 database, with database manipulation facilitated by Knex.
- **Control**: A collection of python scripts dedicated to recording the data from the thermocouples, controlling the heaters, and calculating the thermal conductivity
  - *Thermal Control*: Setting the duty cycle of the heaters based on the control mode set by the user in the website.


## Getting Started

### Prerequisites
- Node.js
- npm or yarn
- SQLite3
- Python 3.11.6
- PicoSDK

### Installation
1. **Clone the repository**:


2. **Install dependencies**:
- For the client:
  ```
  cd client
  npm install
  ```
- For the server:
  ```
  cd server
  npm install
  ```

- **Start the program**
  ```

  python Startup.py
  ```
  
- For the python scripts
  ```
  pip install -r requirements.txt
  ```

3. **Setting up the database**:
- Navigate to the server directory.
- Run the database schema setup scripts.

### Running the Application

- **Start the client**:
cd client
npm start

- **Start the server** (in a new terminal window):
cd server
node server.js

## Usage
Provide instructions on how to use the application, including any available commands, features, and how users can perform key tasks.

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
