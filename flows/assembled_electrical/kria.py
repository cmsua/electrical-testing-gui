import time
import requests
import logging


# Try and connect to the Kria every X s.
def wait_for_kria(address: str, delay: int, data: object) -> None:
    logger = logging.getLogger("kria")
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
    logger = logging.getLogger("kria")
    logger.debug(f"Attempting to power on the the kria at {address}")
    response = requests.put(f"{address}/command", timeout=0.5, json={ "name": "pwr_on" })

    logger.debug(f"Response gotten: {response}")

# Power off the Kria
def disable_kria(address: str, data: object) -> None:
    logger = logging.getLogger("kria")
    logger.debug(f"Attempting to power off the the kria at {address}")
    response = requests.put(f"{address}/command", timeout=0.5, json={ "name": "pwr_off" })

    logger.debug(f"Response gotten: {response}")

def load_firmware(address: str, data: object) -> None:
    logger = logging.getLogger("kria")
    logger.debug(f"Attempting to load firmware on the kria at {address}")
    response = requests.put(f"{address}/command", timeout=0.5, json={ "name": "load_fw" })

    logger.debug(f"Response gotten: {response}")