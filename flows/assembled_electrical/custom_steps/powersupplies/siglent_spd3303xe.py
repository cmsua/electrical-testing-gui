import time
import pyvisa
import logging

import threading
import traceback

logger = logging.getLogger("powersupply")

# Try and connect to the supply every X s.
def wait_for_power_supply(address: str, delay: int, data: object):
    logger.info(f"Waiting on Power Supply at address {address} and delay {delay}")
    rm = pyvisa.ResourceManager()
    while True:
        try:
            # Connect
            logger.debug(f"Connecting to {address}")
            ps = rm.open_resource(address)
            ps.write_termination = "\n"
            ps.read_termination = "\n"

            # Turn Off
            logger.debug("Disabling all tracks")
            ps.write("OUTPut:TRACK 0")
            ps.write("OUTPut CH1,OFF")
            ps.write("OUTPut CH2,OFF")
            ps.write("OUTPut CH3,OFF")

            # Set Initial Values
            logger.debug("Setting up initial voltage/current limits")
            ps.write("CH1:VOLTage 1.5")
            ps.write("CH2:VOLTage 1.5")
            ps.write("CH1:CURRent 3.23")
            ps.write("CH2:CURRent 3.23")

            return {"supply": ps, "lock": threading.Lock()}
        except Exception as e:
            logger.debug(f"Failed to connect to power supply: {e}\n{traceback.format_exc()}")

        time.sleep(delay)

def enable_power_supply(data):
    logger.info("Enabling Channel 1, Aqiring Lock")

    data["_power_supply"]["lock"].acquire()
    logger.debug("Lock acquired")

    data["_power_supply"]["supply"].write("OUTPut CH1,ON")

    data["_power_supply"]["lock"].release()
    logger.debug("Lock Released")

def check_power(data):
    data["_power_supply"]["lock"].acquire()
    
    result = {
        "voltage": float(data["_power_supply"]["supply"].query("MEASure:VOLTage? CH1")),
        "current": float(data["_power_supply"]["supply"].query("MEASure:CURRent? CH1"))
    }

    data["_power_supply"]["lock"].release()

    logger.debug(f"Read from Power Supply: {result}")
    return result

def disable_power_supply(data):
    logger.info("Disabling Channel 1, Aquiring Lock")

    data["_power_supply"]["lock"].acquire()
    logger.debug("Lock acquired")

    data["_power_supply"]["supply"].write("OUTPut CH1,OFF")

    data["_power_supply"]["lock"].release()
    logger.debug("Lock Released")