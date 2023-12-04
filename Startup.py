import subprocess
import pathlib
from aiohttp import web
import aiohttp
import aiohttp_cors
import argparse
import asyncio
import signal
import time
import os

#########################################################################
#SCRIPT VARIABLES
REPO_PICO_TALKER_PATH = "control/Thermal Control/Pico_Talker/Pico_Talker.py"
REPO_READ_DAQ_PATH = "control/Thermocouple/writeFromDAQ.py"
REPO_GRAPH_LIVE_PATH = "control/Thermocouple/graphLive.py"
REPO_GRAPH_FULL_PATH = "control/Thermocouple/graphFull.py"
REPO_SERVER_PATH = "server/server.js"
REPO_CLIENT_PATH = "client/"
REPO_VENV_PY_PATH = "iptc_venv/bin/python3.11"
curr_path = pathlib.Path.cwd()

GIT_REPO_NAME = "In_Plane_Thermal_Conductivity"
TEST_START_ENDPOINT = "/test-start"
END_TEST_ENDPOINT = "/test-end"

PICO_TALKER_LIVE_ENDPOINT = "/script-alive"
GRAPH_LIVE_END_POINT = "/script-alive"

GRAPH_LIVE_PORT = 8123

REPO_BASE_PATH = None

#Process info
PICO_TALKER_PROC = None
GRAPH_LIVE_PROC = None
GRAPH_FULL_PROC = None
SERVER_PROC = None
CLIENT_PROC = None
READ_DAQ_PROC = None

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
ABS_READ_DAQ_PATH = (REPO_BASE_PATH / REPO_READ_DAQ_PATH).as_posix()
ABS_GRAPH_LIVE_PATH = (REPO_BASE_PATH / REPO_GRAPH_LIVE_PATH).as_posix()
ABS_GRAPH_FULL_PATH = (REPO_BASE_PATH/ REPO_GRAPH_FULL_PATH).as_posix()
ABS_VENV_PY_PATH = (REPO_BASE_PATH/REPO_VENV_PY_PATH).as_posix()

#########################################################################
#AIOHTTP
async def startTestHandler(request:web.Request) -> web.StreamResponse:
    """Starts the test off by launching the required files

    Args:
        request (web.Request): request info

    Returns:
        web.StreamResponse: 200 if all scripts exited properly and started properly, 404 and json {process name: pid} if process didnt exit properly or json alive_info
    """
    global PICO_TALKER_PROC, GRAPH_LIVE_PROC, GRAPH_FULL_PROC, READ_DAQ_PROC
    #Dictionary of processes that have an endpoint to make sure that they are running fully
    process_info = {
        "Pico_Talker": {
            "alive_url": f"http://localhost:{PICO_TALKER_NETWORK_PORT}{PICO_TALKER_LIVE_ENDPOINT}",
            "status": 0
        },
        "graphLive": {
            "alive_url": f"http://localhost:{GRAPH_LIVE_PORT}{GRAPH_LIVE_END_POINT}",
            "status": 0
        }
    }
    # Kill Graph Full
    if GRAPH_FULL_PROC is not None: #If graph full is a running process
        GRAPH_FULL_PROC.terminate()
        max_exit = 10
        i = 0
        err = True
        while i<max_exit:
            if GRAPH_FULL_PROC.poll() is None:
                time.sleep(0.5)
                i += 1
            else:
                err = False
                break
        
        if err == True:
            return web.json_response({"graphFull": GRAPH_FULL_PROC.pid}, status=404)

    #Start processes
    PICO_TALKER_PROC = subprocess.Popen(PICO_TALKER_START)
    READ_DAQ_PROC = subprocess.Popen(READ_DAQ_START)
    GRAPH_LIVE_PROC = subprocess.Popen(GRAPH_LIVE_START)
    time.sleep(5)
    return web.Response(status=200)

    # #Ensuring Processes started up well
    # for key in process_info.keys():
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             response = await session.get(process_info[key]["alive_url"], timeout = aiohttp.ClientTimeout(total = 15))
    #             process_info[key]["status"] = int(response.status)
    #     except aiohttp.ClientConnectionError:
    #         process_info[key]["status"] = -1

    # #data to send in return message
    # alive_info = {
    #     "live": [],
    #     "timeout": [],
    #     "error":[],
    #     "conn-refused": []
    # }
    # alive_map = {
    #     200: "live",
    #     404: "error",
    #     0: "timeout",
    #     -1: "conn-refused"
    # }
    # all_good = True
    # for key in process_info.keys():
    #     status = process_info[key]["status"]
    #     alive_info[alive_map[status]].append(key)
    #     if status != 200: #Endpoint has an error
    #         all_good = False
    
    # if all_good == False:
    #     return web.json_response(alive_info, status = 404)
    # else:
    #     return web.json_response(alive_info, status = 200)
    
def endTestHandler(request:web.Request) -> web.StreamResponse:
    """Killing and starting required processes at the end of a test

    Args:
        request (web.Request): 

    Returns:
        web.StreamResponse: 200 if all processes exited properly, 404 if not and returns json of process name and PID of the process that didn't work
    """
    global PICO_TALKER_PROC, GRAPH_FULL_PROC, GRAPH_LIVE_PROC, READ_DAQ_PROC

    #Kill processes
    proc_kill = { #Dictionary of processes to kill
        "Pico_Talker": {
            "proc": PICO_TALKER_PROC,
            "err": True
        },
        "Read_DAQ": {
            "proc": READ_DAQ_PROC,
            "err": True
        },
        "graphLive": {
            "proc": GRAPH_LIVE_PROC,
            "err": True
        }
    }
    
    max_exit = 10
    for key in proc_kill.keys():
        proc_kill[key]["proc"].terminate()
        i = 0
        while i < max_exit:
            if proc_kill[key]["proc"].poll() is None: #If the process is still running reset the loop
                time.sleep(0.5)
                i = i+1
            else:
                proc_kill[key]["err"] = False
                break

    if True in [proc_kill[key]["err"] for key in proc_kill.keys()]: #If one of the processes didn't exit correctly, return a json file of the name of the process and its PID
        errored_proc = {}
        for key in proc_kill.keys():
            if proc_kill[key]["err"] == True:
                errored_proc[key] = proc_kill[key]["proc"].pid
        return web.json_response(errored_proc, status=404)
    
    #Start Processes
    GRAPH_FULL_PROC = subprocess.Popen(GRAPH_FULL_START)

    return web.Response(status=200)
        
def signalGracefulExit(*args):
    """End all the processes when the test is done to make sure that the ports close out nicely
    """
    global SERVER_PROC, CLIENT_PROC, GRAPH_FULL_PROC, GRAPH_LIVE_PROC, PICO_TALKER_PROC, READ_DAQ_PROC
    procs = [SERVER_PROC, CLIENT_PROC, GRAPH_FULL_PROC, GRAPH_LIVE_PROC, PICO_TALKER_PROC, READ_DAQ_PROC]
    for proc in procs:
        proc.terminate()
    os._exit(1)


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

    pico_talker_args = [str(i) for row in [(key, pico_talker_args[key]) for key in pico_talker_args.keys() if pico_talker_args[key] is not None] for i in row]
    
    PICO_TALKER_START = [ABS_VENV_PY_PATH, ABS_PICO_TALKER_PATH]+pico_talker_args
    READ_DAQ_START = [ABS_VENV_PY_PATH, ABS_READ_DAQ_PATH]
    GRAPH_LIVE_START = [ABS_VENV_PY_PATH, ABS_GRAPH_LIVE_PATH]
    GRAPH_FULL_START = [ABS_VENV_PY_PATH, ABS_GRAPH_FULL_PATH]
    NODE_SERVER_START = ["node", ABS_SERVER_PATH]
    NODE_CLIENT_START = ["npm", "start", "--prefix", ABS_CLIENT_PATH]
    UNBUILT_NODE_CLIENT_START = ["npm", "run", "dev", "--prefix", ABS_CLIENT_PATH]


    #Start Up Node Webserver
    SERVER_PROC = subprocess.Popen(NODE_SERVER_START)
    #Start Up Client
    CLIENT_PROC = subprocess.Popen(UNBUILT_NODE_CLIENT_START)
    #Start Up Graph Full
    GRAPH_FULL_PROC = subprocess.Popen(GRAPH_FULL_START)

    #Signal Handler to exit all process
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        signal.signal(s, signalGracefulExit)
    #Event Loop and setup this scripts webserver
    app = web.Application()

    app.router.add_put(TEST_START_ENDPOINT, startTestHandler)
    app.router.add_put(END_TEST_ENDPOINT, endTestHandler)

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*"
        )
    })
    for route in list(app.router.routes()):
        cors.add(route)

    web.run_app(app, host="localhost", port=STARTUP_PORT)