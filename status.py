import logging
import os
import requests

from config import config

def query_hexacontroller_status(hexacontroller) -> dict:
    # Setup Logger
    logger = logging.getLogger(hexacontroller)
    logger.debug("Querying status for " + hexacontroller)

    address = config.getHexacontrollerAddress(hexacontroller)

    # Status Template
    status = {
        "network": None,
        "zynq": None,
        "i2cserver": None,
        "daqserver": None
    }

    # If this is a dummy controller, return nothing
    if not address:
        logger.debug("No address for hexacontroller. Presuming default values...")
        return status

    # Ping IP
    ping = os.system(f"ping -c 1 -W 1 { address} > /dev/null 2>&1")

    if ping == 0:
        status["network"] = True
        logger.debug(f"Ping succeeded with status { ping }")
    else:
        status["network"] = False
        logger.debug(f"Ping failed with status { ping }")
        return status
    
    # Check for Zynq
    zynq_port = config.getHexacontrollerZynqPort(hexacontroller)
    zynq_url = f"http://{ address }:{ zynq_port }" 
    
    try:
        zynq_response = requests.get(zynq_url, timeout=0.01)
        status["zynq"] = True
        logger.debug(f"Zynq is enabled at { zynq_url } with resposne { zynq_response }")
    except Exception as e:
        status["zynq"] = False 
        logger.warn(f"Zynq failed to respond at { zynq_url } with error { e }")
        return status

    # DAQ Server
    daq_status = requests.get(f"{zynq_url}/daq").text
    status["daqserver"] = "Active: active" in daq_status
    if status["daqserver"]:
        logger.debug(f"DAQ Server is running with status { daq_status }")
    else:
        logger.warn(f"DAQ Server is not running with status { daq_status }")

    # I2C Server
    i2c_status = requests.get(f"{zynq_url}/i2c").text
    status["i2cserver"] = "Active: active" in i2c_status
    if status["i2cserver"]:
        logger.debug(f"I2C Server is running with status { i2c_status }")
    else:
        logger.debug(f"I2C Server is not running with status { i2c_status }")

    return status


if __name__ == "__main__":
    print(query_hexacontroller_status("Hexacontroller.One"))