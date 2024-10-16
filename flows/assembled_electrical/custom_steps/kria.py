import time
import requests
import logging


logger = logging.getLogger("kria")

# Try and connect to the Kria every X s.
def wait_for_kria(address: str, delay: int, data: object) -> None:
    while True:
        logger.debug(f"Attempting to connect to the kria at {address}")

        try:
            response = requests.get(address, timeout=0.01)
            logger.debug(f"Recieved response {response}")

            if response.status_code == 404:
                logger.debug(f"Response was successful. Exiting thread.")
                return
        except Exception as e:
            logger.warn(f"Exception when connecting to kria: {e}")

        time.sleep(delay)

# Power on the Kria
def enable_kria(address: str, data: object) -> None:
    logger.debug(f"Attempting to power on the the kria at {address}")
    response = requests.put(f"{address}/command", timeout=0.5, json={ "name": "pwr_on" })

    logger.debug(f"Response gotten: {response}")

# Power off the Kria
def disable_kria(address: str, data: object) -> None:
    logger.debug(f"Attempting to power off the the kria at {address}")
    response = requests.put(f"{address}/command", timeout=0.5, json={ "name": "pwr_off" })

    logger.debug(f"Response gotten: {response}")

# Load firmware onto the board
def load_firmware(address: str, data: object) -> None:
    logger = logging.getLogger("kria")
    logger.debug(f"Attempting to load firmware on the kria at {address}")
    response = requests.put(f"{address}/command", timeout=30, json={ "name": "loadFW" })

    logger.debug(f"Response gotten: {response}")
    
# Restart Services
def restart_services(address: str, delay: int, data: object) -> None:
    logger.debug(f"Attempting to restart on the kria at {address}")
    response = requests.put(f"{address}/command", timeout=0.5, json={ "name": "restart_services" })

    logger.debug(f"Response gotten: {response}")

    # Wait for daq alive
    while True:
        logger.debug(f"Querying DAQ Server status on the kria at {address}")
        response = requests.get(f"{address}/daq", timeout=0.5)
        logger.debug(f"Resposne gotten: {response}")

        if "active (running)" not in response.json()["text"]:
            logger.debug("DAQ not online")
        else:
            logger.debug("DAQ online")
            break

        time.sleep(delay)

    # Wait for i2c alive
    while True:
        logger.debug(f"Querying I2C Server status on the kria at {address}")
        response = requests.get(f"{address}/i2c", timeout=0.5)
        logger.debug(f"Resposne gotten: {response}")

        if "active (running)" not in response.json()["text"]:
            logger.debug("I2C not online")
        else:
            logger.debug("I2C online")
            break

        time.sleep(delay)