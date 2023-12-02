import subprocess
import pathlib
from aiohttp import web
import aiohttp
import argparse
import asyncio
import numpy as np

#########################################################################
#SCRIPT VARIABLES
REPO_PICO_TALKER_PATH = "control/Thermal Control/Pico_Talker/Pico_Talker.py"
REPO_SERVER_PATH = "server/server.js"
REPO_CLIENT_PATH = "client/"
curr_path = pathlib.Path.cwd()

GIT_REPO_NAME = "In_Plane_Thermal_Conductivity"
TEST_START_ENDPOINT = "/test-start"

PICO_TALKER_LIVE_ENDPOINT = "/script-alive"

REPO_BASE_PATH = None

for i, parent in enumerate(reversed(curr_path.as_posix().split('/'))): #Get the base path of the repo repository so that relative paths in the repo can be used
    print(parent, i)
    if parent == GIT_REPO_NAME:
        if i == 0:
            REPO_BASE_PATH = curr_path
        else:
            REPO_BASE_PATH = curr_path.parents[i]
        print(REPO_BASE_PATH)
        break

if REPO_BASE_PATH is None:
    raise FileNotFoundError ("Startup file not in proper git directory")

ABS_PICO_TALKER_PATH = (REPO_BASE_PATH / REPO_PICO_TALKER_PATH).as_posix()
ABS_SERVER_PATH = (REPO_BASE_PATH / REPO_SERVER_PATH).as_posix()
ABS_CLIENT_PATH = (REPO_BASE_PATH / REPO_CLIENT_PATH).as_posix()


#########################################################################
#AIOHTTP
async def startTestHandler(request:web.Request) -> web.StreamResponse:
    """Starts the test off by launching the required files

    Args:
        request (web.Request): request info

    Returns:
        web.StreamResponse: json data from alive_info with either 200 or 404
    """

    #Dictionary of processes that have an endpoint to make sure that they are running fully
    process_info = {
        "Pico_Talker": {
            "alive_url": f"http://localhost:{PICO_TALKER_NETWORK_PORT}{PICO_TALKER_LIVE_ENDPOINT}",
            "status": 0
        }
    }

    #Pico Talker Process
    subprocess.Popen(PICO_TALKER_START)
    # PUT OTHER SUBPROCESSES TO START HERE

    #Ensuring Processes started up well
    for key in process_info.keys():
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(process_info[key]["alive_url"], timeout = aiohttp.ClientTimeout(total = 15))
                process_info[key]["status"] = int(response.status)
        except aiohttp.ClientConnectionError:
            process_info[key]["status"] = -1

    #data to send in return message
    alive_info = {
        "live": [],
        "timeout": [],
        "error":[],
        "conn-refused": []
    }
    alive_map = {
        200: "live",
        404: "error",
        0: "timeout",
        -1: "conn-refused"
    }
    all_good = True
    for key in process_info.keys():
        status = process_info[key]["status"]
        alive_info[alive_map[status]].append(key)
        if status != 200: #Endpoint has an error
            all_good = False
    
    if all_good == False:
        return web.json_response(alive_info, status = 404)
    else:
        return web.json_response(alive_info, status = 200)

#########################################################################
#MAIN

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--startup-port", default=3002, help="Network port that this start up script listens too")
    parser.add_argument("--database", default="your_database.db")
    parser.add_argument("--serial-port", default=None, help="Serial port that the Raspberry Pi Pico PCB is connected to")
    parser.add_argument("--baudrate", default=115200, help="Baud rate the Raspberry Pi Pico PCB communicates with")
    parser.add_argument("--pico-talker-network-port", default = 3001, help="Network port that the Pico Talker script is listening too")
    args = parser.parse_args()
    STARTUP_PORT = args.startup_port
    DATABASE_PATH = args.database
    PCB_SERIAL_PORT = args.serial_port
    PCB_BAUD_RATE = args.baudrate
    PICO_TALKER_NETWORK_PORT = args.pico_talker_network_port

    pico_talker_args = {
        "--database": DATABASE_PATH,
        "--port": PCB_SERIAL_PORT,
        "--baud": PCB_BAUD_RATE
    }

    pico_talker_arg_str = " ".join([str(i) for row in [(key, pico_talker_args[key]) for key in pico_talker_args.keys() if pico_talker_args[key] is not None] for i in row])
    
    PICO_TALKER_START = f'python "{ABS_PICO_TALKER_PATH}" {pico_talker_arg_str}'

    #Start Up Node Webserver
    subprocess.Popen(f"node {ABS_SERVER_PATH}")
    #Start Up Client
    subprocess.Popen(f"npm start --prefix {ABS_CLIENT_PATH}")

    #Event Loop and setup this scripts webserver
    loop = asyncio.get_event_loop()
    app = web.Application()
    app.add_routes([
        web.put(TEST_START_ENDPOINT, startTestHandler)
    ])
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, 'localhost', port = STARTUP_PORT)
    asyncio.ensure_future(site.start())
    loop.run_forever()