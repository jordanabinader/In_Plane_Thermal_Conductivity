# In-Plane Thermal Conductivity Project

## Description
This project integrates various components such as server, database, web application, controls, and computations for in-plane thermal conductivity analysis. It utilizes a robust Node.js server and a responsive front-end built with Next.js.

## Project Structure
- **Client**: Implements the user interface using Next.js and manages HTTP requests with axios.
- **Server**: A Node.js server employing Express.js for HTTP requests and connecting to an SQLite3 database, with database manipulation facilitated by Knex.

## Getting Started

### Prerequisites
- Node.js
- npm or yarn
- SQLite3

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
  node server.js
  ```
  =======
- **Start the program**
  ```
  python Startup.py
  ```
>>>>>>> main

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


