import Serial_Helper
import argparse
import re
import asyncio
import serial_asyncio #Tutorial used: https://tinkering.xyz/async-serial/
import aiosqlite
from collections.abc import Iterable
import time
from datetime import datetime
import math
from functools import partial
from aiohttp import web
import signal
import os
from typing import Tuple, List

#Variables for use inititializing databases
TEST_DIRECTORY_TABLE_NAME = "test_directory"
POWER_TABLE_NAME_BASE = "power_table" #Base strings for the test specific tables that the test name gets appended to with testNameTableFormatter
TEST_SETTING_TABLE_NAME_BASE = "test_settings" #Base strings for the test specific tables that the test name gets appended to with testNameTableFormatter

TEST_SETTING_TABLE_NAME = "" #Filled in by connectDatabase
POWER_TABLE_NAME = "" #Filled in by connectDatabase
POWER_INITIALIZATION_QUERY = "" #Filled in by connectDatabase
TEST_SETTING_INITIALIZATION_QUERY = "" #Filled in by connectDatabase

#Serial Communication Constants (see Serial Communication Pattern.md)
MSG_LEN = 8
HEATER_NOT_FOUND_ERROR = 0x21
DUTY_CYCLE_CHANGE_HEADER = (0x01, 0x02, 0x03) # Heater 1, Heater 2, Both Heaters
INA260_DATA_HEADER = (0x11, 0x12)
TERMINATION = 0xff


#Data to be collected and updated from SQLite Database
control_modes_map = {
    "power":0,
    "temperature":1 #Currently not supported
}
control_mode = 0 #see control_modes_map
control_freq = 0.1 #Hz, desired frequency of the output curve whether that is power or temperature
# duty_cycle = [0, 0] #% duty cycle of each heater, useful for ensuring that the power output lines up properly
control_amplitude = 1 #Amplitude, either in Watts or degrees celcius depending on control mode


#For regex searching
ACCEPTABLE_MSG_HEADERS = bytes() #Flatten acceptable headers, for use in parsing serial messages
for h in [DUTY_CYCLE_CHANGE_HEADER, INA260_DATA_HEADER, HEATER_NOT_FOUND_ERROR]:
    if isinstance(h, Iterable):
        for i in h:
            ACCEPTABLE_MSG_HEADERS += i.to_bytes()
    else:
        ACCEPTABLE_MSG_HEADERS += h.to_bytes()

#Webhook Endpoints
TEST_SETTING_ENDPOINT = "/test-setting-update"
END_TEST_ENDPOINT = "/test-end"


class SerialComm(asyncio.Protocol):
    def __init__(self, power_queue:asyncio.Queue, test_setting_queue:asyncio.Queue, db:aiosqlite.Connection, network_port:int = 3001, heater_scalar:Tuple[float, float] = (1,1), heater_resitance: Tuple[float, float] = (0.05, 0.05), supply_voltage:float = 12):
        """Class for managing serial communicaiton with the raspberry pi pico power distribution and control PCB
        Source for this method of using functools.partial: https://tinkering.xyz/async-serial/#the-rest
        Args:
            power_queue (asyncio.Queue): Queue instance that stores the data from the INA260 voltage and current monitoring
            test_setting_queue (asyncio.Queue): Queue instance for updating test settings
            db (aiosqlite.Connection): The database storing all the info for the test setup
            network_port (int, optional): Network port for the webserver to listen to for test setting and test end requests. Defaults to 3001.
            heater_scalar (Tuple[float, float], optional): (heater 0, heater 1),heaters are going to have different thermal masses as bottom heater has more to heat up so having a scalar would allow both blocks to heat similarly. Defaults to (0,0).
            heater_resitance (Tuple[float, float], optional): Ohms, (heater 0, heater 1), measured value, as different heaters are going to have different resistances. Defaults to (0.05, 0.05).
            supply_voltage (float, optional): Volts, The supply voltage that drives the heaters. Defaults to 12.
        """

        super().__init__()
        self.transport = None
        self.db = db
        #Queues
        self.test_setting_queue = test_setting_queue
        self.power_queue = power_queue
        
        #Test Setup info
        self.duty_cycle = [0, 0] #% duty cycle of each heater, useful for ensuring that the power output lines up properly
        self.HEATER_RESISTANCE = heater_resitance
        self.HEATER_SCALAR = heater_scalar
        self.SUPPLY_VOLTAGE = supply_voltage
        self.HEATERS = (0, 1) # Mapping for heater numbers
        self.DUTY_CYCLE_UPDATE_PERIOD = 0.1 # Seconds

        #Webpage network info
        self.port = network_port

        #Test Setting Information
        self.CONTROL_OPTIONS = {
            "Manual": self.heaterManual,  # Parse db table amplitude column as duty cycle in percent to send to serial device
            "Power": self.heaterPower     # Sine wave of power, Amplitude column in watts, frequency column in rad/s
            #, "Temperature": self.heaterTemp # Possible addtion of temperature control in the future, needs a PID loop to ensure temperatures are accurate. Amplitude is amplitude of temp sine, frequency in rad/s, would need to add a new column for the vertical offset.
        }
        self.control_mode = "Manual" # Default Setting so that the test starts off with all the heaters off
        self.frequency = 0 #Rad/s
        self.amplitude = 0 # units depend on control mode, see self.CONTROL_OPTIONS
        self.start_time = time.time()

    #########################################################################
    #Serial Communication
    def connection_made(self, transport:serial_asyncio.SerialTransport):
        """Gets called when serial is connected, inherited function

        Args:
            transport (serial_asyncio.SerialTransport): input gets passed by erial_asyncio.create_serial_connection()
        """
        self.transport = transport
        self.pat = b'['+ACCEPTABLE_MSG_HEADERS+b'].{'+str(MSG_LEN-2).encode()+b'}'+TERMINATION.to_bytes()
        self.read_buf = bytes()
        self.bytes_recv = 0
        self.msg = bytearray(MSG_LEN)
        print("SerialReader Connection Created")
        webserver_task = asyncio.ensure_future(self.initWebserver())
        webserver_task.set_name("Webserver-Task")
        control_loop_task = asyncio.ensure_future(self.controlLoop())
        control_loop_task.set_name("Control-Loop-Task")

        self.heater_control_task = asyncio.ensure_future(self.stall()) #The Function that is inside this task gets controlled by self.controlLoop
        self.heater_control_task.set_name("Heater-Control-Task")

    def connection_lost(self, exc:Exception):
        """Gets called when serial is disconnected/lost, inherited function

        Args:
            exc (Exception): Thrown exception
        """
        print(f"SerialReader Closed with exception: {exc}")
    
    async def parseMsg(self, msg:bytes):
        """Parse a message sent by the raspberry pi pico and add it the proper queue to get put into the database

        Args:
            msg (bytes): bytes object of length MSG_LEN that matched the self.pat
        """
        if msg[0] == INA260_DATA_HEADER[0]: #INA260 Data Heater 0
            mV = ((((msg[1]<<8)+msg[2])<<8)+msg[3])/100
            mA = ((((msg[4]<<8)+msg[5])<<8)+msg[6])/100
            print(f"Heater 0: {mV} mV | {mA} mA")
            await self.power_queue.put([0, mV, mA, self.duty_cycle[0], datetime.now().__str__()])

        elif msg[0] == INA260_DATA_HEADER[1]: #INA260 Data Heater 1
            mV = ((((msg[1]<<8)+msg[2])<<8)+msg[3])/100
            mA = ((((msg[4]<<8)+msg[5])<<8)+msg[6])/100
            print(f"Heater 1: {mV} mV | {mA} mA")
            await self.power_queue.put([1, mV, mA, self.duty_cycle[1], datetime.now().__str__()]) 
    
    def data_received(self, data):
        """add data sent over serial to the serial buffer and check for properly formatted messages using regex, then pass the message to parseMsg

        Args:
            data (bytes): _description_
        """
        # print("Reached Data Recieved")
        self.read_buf += data
        # print(self.read_buf)
        if len(self.read_buf)>= MSG_LEN:
            while True:
                match = re.search(self.pat, self.read_buf)
                if match == None:
                    break
                else:
                    asyncio.ensure_future(self.parseMsg(match.group(0)))
                    self.read_buf = self.read_buf[match.end():]
                    # print(self.read_buf)

    def sendDutyCycleMsg(self, heater:int):
        """format the duty cycle info and send to raspberry pi pico

        Args:
            heater (int): 0: Heater 0 only, 1: Heater 1 only, 2: both heaters in the same message, 0 or 1 would only really be useful for thermal control
        """
        self.msg[0] = DUTY_CYCLE_CHANGE_HEADER[heater]
        if heater == 2: #Send duty cycle update to both heaters
            self.msg[1:4] = int(self.duty_cycle[0]*1000).to_bytes(3)
            self.msg[4:7] = int(self.duty_cycle[1]*1000).to_bytes(3)
        else:
            self.msg[1:4] = int(self.duty_cycle[heater]*1000).to_bytes(3)

        self.sendMsg()

    def sendMsg(self):
        """Add the data into the serial output buffer
        """
        self.transport.write(self.msg)


    #########################################################################
    #Webserver
    async def initWebserver(self):
        """Initialize aiohttp webserver for get notified when test settings are updated or the test is over
        """
        # Webserver
        app = web.Application()
        app.add_routes([
            web.put(TEST_SETTING_ENDPOINT, self.testSettingUpdateHook),
            web.put(END_TEST_ENDPOINT, self.endTestHook)
        ])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port=self.port)
        try:
            await site.start()
        except asyncio.CancelledError:
            runner.shutdown()
            app.cleanup()

    async def testSettingUpdateHook(self, request:web.Request)-> web.StreamResponse:
        """handler for PUT requests at TEST_SETTING_ENDPOINT endpoint

        Args:
            request (web.Request): content of the put request, doesn't really matter for this

        Returns:
            web.StreamResponse: responds with 200 status
        """
        curr_setting = await self.getLatestTestSetting()
        print("/test-setting-update put request")
        await self.test_setting_queue.put(curr_setting)
        return web.Response(status=200)
    
    async def getLatestTestSetting(self)->Tuple:
        """Gets the most recently added line in the test setting table

        Returns:
            Tuple: test setting database table row, (control mode, frequency, amplitude, datetime)
        """
        curr_setting = await self.db.execute_fetchall(f"SELECT * FROM {TEST_SETTING_TABLE_NAME} ORDER BY datetime DESC LIMIT 1 ")
        curr_setting = curr_setting[0]
        return curr_setting

    async def endTestHook(self, request:web.Request)-> web.StreamResponse:
        """_summary_

        Args:
            request (web.Request): content of the put request, doesn't really matter for this

        Returns:
            web.StreamResponse: responds with 200 status
        """
        signal.raise_signal(signal.SIGINT) #Raise signal.SIGINT to get caught by signalGracefulExit
        return web.Response(status=200)

    
    #########################################################################
    #Heater Control Loops
    async def controlLoop(self):
        """Infinite loop to change the test settings based on items getting added to the test setting queue
        """
        latest = await self.getLatestTestSetting()
        await self.test_setting_queue.put(latest) #Put the desired initial settings into the test setting queue to get applied at the beginning of the test
        try:
            while True:
                new_test_setting = await self.test_setting_queue.get()
                control_mode = new_test_setting[0]
                frequency = new_test_setting[1]
                amplitude = new_test_setting[2]

                if control_mode in self.CONTROL_OPTIONS.keys(): #Make sure the control mode is valid
                    if control_mode == self.control_mode and frequency == self.frequency and amplitude == self.amplitude: #If all the settings are the same do nothing
                        print("Duplicate Test Setting Update")
                        continue
                    else: #If something has changed
                        #Cancel the currently running task
                        self.heater_control_task.cancel()
                        await self.heater_control_task

                        #Start the new task
                        print(f"New Control Mode: {control_mode}, Amplitude: {amplitude}, Frequency: {frequency}")
                        self.control_mode = control_mode
                        self.frequency = frequency
                        self.amplitude = amplitude
                        self.start_time = time.time() #Reset the clock for start time, useful for sine wave
                        self.heater_control_task = asyncio.ensure_future(self.CONTROL_OPTIONS[control_mode]())

        except asyncio.CancelledError:
            self.heater_control_task.cancel() #Cancel the current heater control task first to ensure that the heaters are all turned off
            await self.heater_control_task #Wait for that task to finish before closing the serial port
            self.transport.close() # self.controlLoop should only get exited when 
            print("Control Loop Exited")
            return
     
    async def stall(self):
        """Loop to be used similar to heaterPower or heaterManual, however this one just does nothing. used when first starting the system up
        """
        print("Entered Stall Control Mode")
        try: 
            while True:
                await asyncio.sleep(0.5) #This should stay relatively short to ensure that when it gets cancelled it can cancel quickly
        except asyncio.CancelledError:
            return

    async def heaterPower(self):
        """Coroutine to infinitely loop and calculate the duty cycle of the heaters for the raspberry pi pico using a power sin wave
        """
        print("Heater Control Mode Entered")
        print(self.frequency, self.control_mode, self.amplitude)
        try:
            while True:
                await asyncio.sleep(self.DUTY_CYCLE_UPDATE_PERIOD) #pause duty cycle update for a bit while being non-blocking
                curr_time = time.time()
                for heater in self.HEATERS:
                    self.duty_cycle[heater] = math.sqrt(self.HEATER_SCALAR[heater]*self.HEATER_RESISTANCE[heater]*(self.amplitude*math.sin(self.frequency*(curr_time-self.start_time)/(2*math.pi))+self.amplitude))*100/self.SUPPLY_VOLTAGE
                
                self.sendDutyCycleMsg(2)
                print(f"Time: {curr_time-self.start_time} Heater 0: {self.duty_cycle[0]} Heater 1: {self.duty_cycle[1]}")

        except asyncio.CancelledError: #when .cancel() is called for this coroutine
            self.duty_cycle = [0, 0]
            self.sendDutyCycleMsg(2)
            print("Heater Control Task Power Sine Exited")
    
    async def heaterManual(self):
        """Coroutine to set the duty cycle of both heaters to the value stored in self.amplitude. Example: self.amplitude = 3.55, duty cycle set to 3.55*
        """
        print("Entered Manual Control Mode")
        try:
            for heater in self.HEATERS:
                self.duty_cycle[heater] = self.amplitude
            self.sendDutyCycleMsg(2)

            while True:
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            self.duty_cycle = [0, 0]
            self.sendDutyCycleMsg(2)
            print("Heater Control Task Manual Exited")


#########################################################################
#AIOSQLITE
async def connectDatabase(db:str) -> aiosqlite.Connection:
    """ Connect to the sqlite database and initialize requires tables

    Args:
        db (str): database string, example: my_database.db

    Returns:
        aiosqlite.Connection: databse connection
    """
    database = await aiosqlite.connect(db)
    test_name = await database.execute_fetchall(f"SELECT testId FROM {TEST_DIRECTORY_TABLE_NAME} ORDER BY datetime DESC LIMIT 1")
    test_name = test_name[0][0]

    #Set proper table names for this test
    global POWER_INITIALIZATION_QUERY, TEST_SETTING_INITIALIZATION_QUERY, TEST_SETTING_TABLE_NAME, TEST_SETTING_TABLE_NAME_BASE, POWER_TABLE_NAME, POWER_TABLE_NAME_BASE
    POWER_INITIALIZATION_QUERY = createPowerInitQuery(test_name)
    TEST_SETTING_INITIALIZATION_QUERY = createTestSettingInitQuery(test_name)
    TEST_SETTING_TABLE_NAME = testNameTableFormatter(TEST_SETTING_TABLE_NAME_BASE, test_name)
    POWER_TABLE_NAME = testNameTableFormatter(POWER_TABLE_NAME_BASE, test_name)

    #Create power table if it doesn't already exist
    await database.execute(POWER_INITIALIZATION_QUERY)
    #Create test_settings table if it doesn't already exist
    await database.execute(TEST_SETTING_INITIALIZATION_QUERY)

    return database

def testNameTableFormatter(table_name:str, test_name:str)-> str:
    """Returns the properly formatted table name string for all tables

    Args:
        table_name (str): Base name of the table, like test_settings
        test_name (str): name of the test

    Returns:
        str: table name for this specific test
    """
    return f"{table_name}_{test_name}"

def createPowerInitQuery(test_name:str)->str:
    """create the proper table creation query for the power data

    Args:
        test_name (str): name of the test

    Returns:
        str: proper query
    """

    ret = f'''
    CREATE TABLE IF NOT EXISTS {testNameTableFormatter(POWER_TABLE_NAME_BASE, test_name)} (
    heaterNum REAL NOT NULL,
    mV REAL NOT NULL,
    mA REAL NOT NULL,
    dutyCycle REAL NOT NULL,
    datetime REAL NOT NULL
    )
    '''
    return ret

def createTestSettingInitQuery(test_name:str)->str:
    """create the proper table creation query for the test settings

    Args:
        test_name (str): name of the test

    Returns:
        str: proper query
    """
    ret = f'''
    CREATE TABLE IF NOT EXISTS {testNameTableFormatter(TEST_SETTING_TABLE_NAME_BASE, test_name)} (
    controlMode REAL NOT NULL,
    frequency REAL NOT NULL,
    amplitude REAL NOT NULL,
    datetime REAL NOT NULL
    )
    '''
    return ret

async def powerQueueHandler(database:aiosqlite.Connection, power_table_name:str, powerqueue:asyncio.Queue):
    """Coroutine to infinietly loop and put INA260 data into the proper sqlite database table

    Args:
        database (aiosqlite.Connection):
        power_table_name (str): name of the table for power data inside primary sqlite database
        powerqueue (asyncio.Queue): queue that feeds all the INA260 data between coroutines
    """
    try:
        while True:
            pwr_data = await powerqueue.get()
            await database.execute(f"INSERT INTO {power_table_name} (heaterNum, mV, mA, dutyCycle, datetime) VALUES ({pwr_data[0]}, {pwr_data[1]}, {pwr_data[2]}, {pwr_data[3]}, '{pwr_data[4]}')")
            await database.commit()
    except asyncio.CancelledError:
        print("Power Queue Shutting Down")


#########################################################################
#Signal Handling and Graceful Exit
def signalGracefulExit(*args):
    """function for signal handling, calls graceful exit when triggered.

    Args:
        stack_frame (frame object or none): see https://docs.python.org/3/library/signal.html#signal.signal 
        loop (asyncio.AbstractEventLoop): primary event loop
    """
    gracefulExit(loop)

def gracefulExit(loop:asyncio.AbstractEventLoop):
    """Gracefully exit whatevent loops can be gracefully exited, some, like the serial coroutine might not be so pleasant, based on https://www.roguelynn.com/words/asyncio-graceful-shutdowns/

    Args:
        loop (asyncio.AbstractEventLoop): primary event loop
    """
    graceful_exit_req_tasks = ["Control-Loop-Task"] #Tasks that require a graceful exit, should be in order of exit priority, Control-Loop-Task ensures that the serial port gets closed out correctly
    # tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    # print("Tasks at the beginning: ")
    # for t in tasks:
    #     print(t)

    #Ensure that task writing duty cycle data gets canceled first because otherwise the heaters could be left on
    serial_out_tasks = [t for t in asyncio.all_tasks() if t._coro.__name__ in graceful_exit_req_tasks]
    for t in serial_out_tasks:
        t.cancel()

    #Cancel the rest of the tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
   

#########################################################################
#Main
async def createMainCoroutines(loop:asyncio.AbstractEventLoop, serial_port:str, baud_rate:int, db:aiosqlite.Connection):
    """This function creates all the required coroutines to enable to use of run_until_complete to clean up exiting of the program

    Args:
        loop (asyncio.AbstractEventLoop): main event loop
        serial_port (str): serial port string
        baud_rate (int): boud rate of the serial port
        db (aiosqlite.Connection): primary data base for power and test setting data
    """
    power_queue = asyncio.Queue() #Power queue items should be a list with the following structure: (Heater Number, mV, mA, duty cycle, time)
    test_setting_queue = asyncio.Queue() #Test setting queue to pass updated test settings through

    #initalize Serial Asyncio reader and writer
    serial_with_queue = partial(SerialComm, power_queue = power_queue, test_setting_queue = test_setting_queue, db =  db)
    serial_coro = serial_asyncio.create_serial_connection(loop, serial_with_queue, serial_port, baudrate=baud_rate)
    serial_task = asyncio.ensure_future(serial_coro)
    serial_task.set_name("Serial-Comm-Task")
    print("SerialComm Scheduled")

    #Initialize powerQueueHandler coroutines
    power_queue_task = asyncio.ensure_future(powerQueueHandler(db, POWER_TABLE_NAME, power_queue))
    power_queue_task.set_name("Power-Queue-Task")
    print("powerQueueHandler Scheduled")

    
    try:
        # await asyncio.gather(serial_task, power_queue_task)
        await asyncio.gather(serial_task, power_queue_task)
    except asyncio.CancelledError:
        print("createMainCoroutines Cancelled")        


if __name__ == "__main__":
    # Argument parsing for serial port
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=None)
    parser.add_argument("--baud", default=115200)
    parser.add_argument("--database", default='your_database.db')
    args = parser.parse_args()
    port = args.port
    baud = args.baud
    database = args.database

    # If no port is given, use Serial_Helper to choose one
    if port is None:
        port = Serial_Helper.terminalChooseSerialDevice()
    #If port given doesn't exist, use Serial_Helper
    elif Serial_Helper.checkValidSerialDevice(port) is False:
        Serial_Helper.terminalChooseSerialDevice()

    # Separate loop required to properly initialize the database before moving on to the rest of the code.
    loop = asyncio.get_event_loop()
    db = asyncio.ensure_future(connectDatabase(database))
    loop.run_until_complete(db)
    db = db.result()

    # New eventloop that runs forever to handle the bulk of this script
    loop = asyncio.get_event_loop()

    #Add signal handler tasks
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        signal.signal(s, signalGracefulExit)
    
    create_main_task = asyncio.ensure_future(createMainCoroutines(loop, port, baud, db))
    
    loop.run_until_complete(create_main_task)
    print("Exited Loop")
    loop.close()
    os._exit(1)
