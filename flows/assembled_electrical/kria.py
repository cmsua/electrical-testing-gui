from PyQt6.QtCore import QThread

from flows.steps import ThreadStep

import time
import requests
import logging


# Try and connect to the Kria every X s.
class ConnectKriaThread(QThread):
    def __init__(self, address: str, delay: float) -> None:
        super().__init__()
        self._address = address
        self._delay = delay

    def run(self) -> None:
        logger = logging.getLogger("kria")
        while True:
            logger.debug(f"Attempting to connect to the kria at {self._address}")

            try:
                response = requests.get(self._address, timeout=0.01)
                logger.debug(f"Recieved response {response}")

                if response.status_code == 404:
                    logger.debug(f"Response was successful. Exiting thread.")
                    return
            except Exception as e:
                logger.warn(f"Exception when connecting to kria: {e}")

            time.sleep(self._delay)


# Connect to a kria task
class ConnectKriaStep(ThreadStep):
    def __init__(self, name: str, address: str, delay: float,
                 message: str) -> None:
        super().__init__(name, message, ConnectKriaThread(address, delay))

# Try and connect to the Kria every X s.
class EnableKriaThread(QThread):
    def __init__(self, address: str) -> None:
        super().__init__()
        self._address = address

    def run(self) -> None:
        logger = logging.getLogger("kria")
        logger.debug(f"Attempting to power on the the kria at {self._address}")
        response = requests.put(f"{self._address}/command", timeout=0.5, json={ "name": "pwr_on" })

        logger.debug(f"Response gotten: {response}")


# Connect to a kria task
class EnableKriaStep(ThreadStep):
    def __init__(self, name: str, address: str, message: str) -> None:
        super().__init__(name, message, EnableKriaThread(address))
        
# Try and connect to the Kria every X s.
class DisableKriaThread(QThread):
    def __init__(self, address: str) -> None:
        super().__init__()
        self._address = address

    def run(self) -> None:
        logger = logging.getLogger("kria")
        logger.debug(f"Attempting to power off the the kria at {self._address}")
        response = requests.put(f"{self._address}/command", timeout=0.5, json={ "name": "pwr_off" })

        logger.debug(f"Response gotten: {response}")


# Connect to a kria task
class DisableKriaStep(ThreadStep):
    def __init__(self, name: str, address: str, message: str) -> None:
        super().__init__(name, message, DisableKriaThread(address))