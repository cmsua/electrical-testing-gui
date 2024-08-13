from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton

from flows.objects import TestStep, TestWidget
from flows.steps import ThreadStep

import time
import requests
import os


# Try and connect to the Kria every X s.
class ConnectKriaThread(QThread):
    def __init__(self, address: str, delay: float) -> None:
        super().__init__()
        self._address = address
        self._delay = delay

    def run(self) -> None:
        while True:
            try:
                response = requests.get(self._address, timeout=0.01)
                if response.status_code == 404:
                    return
            except:
                pass

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
        requests.put(f"{self._address}/command", timeout=0.05, json={ "name": "pwr_on" })


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
        requests.put(f"{self._address}/command", timeout=0.05, json={ "name": "pwr_off" })


# Connect to a kria task
class DisableKriaStep(ThreadStep):
    def __init__(self, name: str, address: str, message: str) -> None:
        super().__init__(name, message, DisableKriaThread(address))