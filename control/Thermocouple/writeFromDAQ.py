import sqlite3
import ctypes
import time
from picosdk.usbtc08 import usbtc08 as tc08
from picosdk.functions import assert_pico2000_ok

OPEN_CHANNELS = 2  # 2 TCs, opens 2 Channels + CJ = 3. Keep at 2.
CHANNELS_TO_ADD = 6  # +6 TCs gets to 8 Channels open. Maximum of 6.
CYCLES_UNTIL_LARGE_READ = 50
TC_LAG = 0.068
PRINT_LOG = False
DATABASE_NAME = 'server/angstronomers.sqlite3'
TEST_DIR_TABLE_NAME = "test_directory"
TEST_ID = "1"  # TODO
TABLE_NAME = "temperature_table_" + TEST_ID

# Connect to the database
conn = sqlite3.connect(DATABASE_NAME)

# Create a cursor
cursor = conn.cursor()

# Create a table
# cursor.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
#                 date_time TEXT DEFAULT CURRENT_TIMESTAMP,
#                 relTime REAL NOT NULL,
#                 temp1 REAL NOT NULL,
#                 temp2 REAL NOT NULL,
#                 temp3 REAL,
#                 temp4 REAL,
#                 temp5 REAL,
#                 temp6 REAL,
#                 temp7 REAL,
#                 temp8 REAL)''')

# Get Test ID
cursor.execute(f'''SELECT testId
                FROM {TEST_DIR_TABLE_NAME}
                ORDER BY testId DESC
                LIMIT 1''')
resultstid = cursor.fetchall()
TEST_ID = str(resultstid[0][0])
TABLE_NAME = "temperature_table_" + TEST_ID

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# open unit
status["open_unit"] = tc08.usb_tc08_open_unit()
assert_pico2000_ok(status["open_unit"])
chandle = status["open_unit"]

# set mains rejection to 50 Hz
status["set_mains"] = tc08.usb_tc08_set_mains(chandle, 0)
assert_pico2000_ok(status["set_mains"])

# set up channel
# thermocouples types and int8 equivalent
# B=66 , E=69 , J=74 , K=75 , N=78 , R=82 , S=83 , T=84 , ' '=32 , X=88
typeK = ctypes.c_int8(75)
typeNA = ctypes.c_int8(32)
for i in range(OPEN_CHANNELS):
    status["set_channel"] = tc08.usb_tc08_set_channel(chandle, i + 1, typeK)
assert_pico2000_ok(status["set_channel"])

# Set up variables to read temperature
temp = (ctypes.c_float * 9)()
overflow = ctypes.c_int16(0)
units = tc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]

print(status)

input("Press Enter to continue...")

print("Going!")

# Set up variables for timing, loop control
start_time = time.time()
large_read_counter = 0
vals_to_print = OPEN_CHANNELS + 1

# Loop to collect temperature data
while 1:
    # Increment counter until reading of more TCs
    large_read_counter += 1

    # Large TC Read
    if large_read_counter == CYCLES_UNTIL_LARGE_READ:
        vals_to_print = OPEN_CHANNELS + CHANNELS_TO_ADD + 1
        # Add Channels
        for i in range(OPEN_CHANNELS, OPEN_CHANNELS + CHANNELS_TO_ADD):
            tc08.usb_tc08_set_channel(chandle, i + 1, typeK)
        # Take TC Measurements
        end_time = time.time()  # Must be right before get_single reading
        tc08.usb_tc08_get_single(chandle, ctypes.byref(temp), ctypes.byref(overflow), units)
        elapsed_time = end_time - start_time
        # Insert Values
        cursor.execute(f"INSERT INTO {TABLE_NAME} (relTime, temp1, temp2, temp3, temp4, temp5, temp6, temp7, temp8) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (elapsed_time, temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], temp[7], temp[8]))

    # Normal (2) TC Read
    else:
        # Reset Large Read channels set to Normal Read
        if large_read_counter == CYCLES_UNTIL_LARGE_READ + 1:
            large_read_counter = 0
            vals_to_print = OPEN_CHANNELS + 1
            for i in range(OPEN_CHANNELS, OPEN_CHANNELS + CHANNELS_TO_ADD):
                tc08.usb_tc08_set_channel(chandle, i + 1, typeNA)
        # Take Measurements
        end_time = time.time()
        tc08.usb_tc08_get_single(chandle, ctypes.byref(temp), ctypes.byref(overflow), units)
        elapsed_time = end_time - start_time
        # Insert Values
        cursor.execute(f"INSERT INTO {TABLE_NAME} (relTime, temp1, temp2) VALUES (?, ?, ?)",
                       (elapsed_time, temp[1], temp[2]))

    if PRINT_LOG:
        for channel in range(vals_to_print):
            true_elapsed_time = elapsed_time + (TC_LAG * max(1, channel))
            print(f"Channel {channel}: {temp[channel]}, Time: {true_elapsed_time}")

    # Commit the changes to the database
    conn.commit()

# close unit
status["close_unit"] = tc08.usb_tc08_close_unit(chandle)
assert_pico2000_ok(status["close_unit"])

# Close the cursor and the connection
cursor.close()
conn.close()
