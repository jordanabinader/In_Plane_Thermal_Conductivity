import serial
import serial.tools
import serial.tools.list_ports
from typing import List, Dict

def terminalChooseSerialDevice(): #Typing should be List[serial.tools.list_ports.ListPortInfo] but python is throwing an absolute fit because it can't seem to import the class properly. 
    """ List the valid serial ports and get user input on which one to use for the function

    Args:
        ports (List[serial.tools.list_ports.ListPortInfo]): List of serial ports that are valid devices to communicate with
    """
    ports = serial.tools.list_ports.comports()
    valid_input = False
    bad_inputs = 0
    num_ports = len(ports)
    if num_ports < 1:
        raise BaseException("Computer has no connected serial devices")

   
    while valid_input is False:
        if bad_inputs%3 == 0: # Reprint port options every third bad input to not clog up the terminal
            for i, port in enumerate(ports, 1):
                print("[Index] Device Path/COM Port | Manufacturer | Description")
                print(f"[{i}] {port.device} | {port} | {port.manufacturer} | {port.description}")
        
        dev = input(f"Select which Serial Device to use [1-{num_ports}]: ")

        try:
            if float(dev) == int(dev) and int(dev) in range(1, num_ports+1): #Make sure input was solely an integer and in the accpetable range
                return ports[int(dev)-1].device
            else:
                print(f"Number was not acceptable, please input a whole number from 1 to {num_ports}")
                bad_inputs += 1
        except ValueError:
            print(f"Input was not acceptable, please input a whole number from 1 to {num_ports}")
            bad_inputs += 1

def checkValidSerialDevice(check_port):
    ports = serial.tools.list_ports.comports()
    if len(ports) < 1:
        raise BaseException("Computer has no connected serial devices")

    ports_devs = [i.device for i in ports]
    return (check_port in ports_devs)

if __name__ == "__main__":
    terminalChooseSerialDevice()