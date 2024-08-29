import time
import pyvisa
import logging

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

            return ps
        except:
            pass

        time.sleep(delay)

def enable_power_supply(data):
    logger.info("Enabling Channel 1")
    data["power_supply"].write("OUTPut CH1,ON")


def check_power(data):
    result = {
        "voltage": float(data["power_supply"].query("MEASure:VOLTage? CH1")),
        "current": float(data["power_supply"].query("MEASure:CURRent? CH1"))
    }

    logger.info(f"Read from Power Supply: {result}")
    return result

def disable_power_supply(data):
    logger.info("Disabling Channel 1")
    data["power_supply"].write("OUTPut CH1,OFF")