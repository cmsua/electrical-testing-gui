from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel

import logging
import os
import requests
import time
from functools import partial

from .custom_steps import powersupply

logger = logging.getLogger("watcher")

pulled_labels = ["DAQ Client",
          "Kria", "Power Supply"]

def check_status(status, _):
    if status == "PASS" or status == True:
        return ["Passed", "green"]
    elif status == "FAIL" or status == False:
        return ["Failed", "red"]
    else:
        return [f"Unknown: {status}", "blue"]

def pedestal_run_validator(key, _, data):
    noisy = int(data[key + "NUMBER_CHANNELS_NOISE_MORE2"])
    dead = int(data[key + "NUMBER_CHANNELS_NOISE_AT0"])

    color = "green"
    if noisy > 0 and noisy < 2:
        color = "gold"
    elif dead > 0 and dead < 2:
        color = "gold"
    elif noisy > 2 or dead > 2:
        color = "red"

    return [f"{noisy} Noisy, {dead} Dead", color]

data_labels = {
    "Test Status": {
        "key": "TEST_SUCCESS",
        "validator": check_status
    },
    "Power (Default)": {
        "key": "POWER:DEFAULT",
        "validator": lambda val, data: [str(val), "green"] if True else [str(val), "red"] #TODO I heard about a success/fail value but never seen it impl
    },
    "Power (Configured)": {
        "key": "POWER:CONFIGURED",
        "validator": lambda val, data: [str(val), "green"] if True else [str(val), "red"] #TODO I heard about a success/fail value but never seen it impl
    },
    "I2C Checker (Default)": {
        "key": "I2C_CHECKER:DEFAULT",
        "validator": check_status
    },
    "I2C Checker (Configured)": {
        "key": "I2C_CHECKER:CONFIGURED",
        "validator": check_status
    },
    "Pedestal Run 0-0 Status": {
        "key": "PEDESTAL_RUN:0:0:NUMBER_CHANNELS_NOISE_AT0",
        "validator": partial(pedestal_run_validator, "PEDESTAL_RUN:0:0:")
    },
    "Pedestal Run 0-1 Status": {
        "key": "PEDESTAL_RUN:0:0:NUMBER_CHANNELS_NOISE_AT0",
        "validator": partial(pedestal_run_validator, "PEDESTAL_RUN:0:1:")
    },
    "Pedestal Run 1-0 Status": {
        "key": "PEDESTAL_RUN:0:0:NUMBER_CHANNELS_NOISE_AT0",
        "validator": partial(pedestal_run_validator, "PEDESTAL_RUN:1:0:")
    },
    "Pedestal Run 1-1 Status": {
        "key": "PEDESTAL_RUN:0:0:NUMBER_CHANNELS_NOISE_AT0",
        "validator": partial(pedestal_run_validator, "PEDESTAL_RUN:1:1:")
    },
    "Pedestal Run 2-0 Status": {
        "key": "PEDESTAL_RUN:0:0:NUMBER_CHANNELS_NOISE_AT0",
        "validator": partial(pedestal_run_validator, "PEDESTAL_RUN:2:0:")
    },
    "Pedestal Run 2-1 Status": {
        "key": "PEDESTAL_RUN:0:0:NUMBER_CHANNELS_NOISE_AT0",
        "validator": partial(pedestal_run_validator, "PEDESTAL_RUN:2:1:")
    },
    "Pedestal Run Corruption": {
        "key": "PEDESTAL_RUN:CORRUPTION",
        "validator": check_status
    }
}

class WatcherThread(QThread):
    output = pyqtSignal(object)
    def __init__(self, kria_address, data):
        super().__init__()

        self.kria_address = kria_address
        self.data = data

    def run(self):
        try:
            status = {}
            not_initialized = ["Not Initialized", "gold"]
            
            # Check Local DAQ
            try:
                daq_status = os.popen("systemctl status daq-client").read()
                daq_status = daq_status.split("Active: ")[1].split(" since")[0]
                logger.debug(f"Recieved daq-client status {daq_status}")

                status["DAQ Client"] = [daq_status, "green" if daq_status == "active (running)" else "red"]
            except Exception as exception:
                logger.critical(f"DAQ Client Status Failed: {exception}")
                status["DAQ Client"] = ["Error!", "red"]
                

            # Check Kria Services
            try:
                daq_response = requests.get(f"{self.kria_address}/daq", timeout=0.3).json()["text"].split("Active: ")[1].split(" since")[0]
                logger.debug(f"Recieved daq-server status {daq_response}")

                i2c_response = requests.get(f"{self.kria_address}/daq", timeout=0.3).json()["text"].split("Active: ")[1].split(" since")[0]
                logger.debug(f"Recieved i2c-server status {i2c_response}")

                text = f"I2C: {i2c_response}, DAQ: {daq_response}"
                color = "green" if i2c_response == "active (running)" and daq_response == "active (running)" else "red"
                status["Kria"] = [text, color]
            except requests.exceptions.Timeout as exception:
                logger.critical(f"Request timed out: {exception}")
                status["Kria"] = ["Timed Out", "red"]

            # Check Power Supply
            try:
                if "_power_supply" in self.data:
                    result = powersupply.check_power(self.data)
                    voltage = result["voltage"]
                    current = result["current"]

                    logger.debug(f"Read Power Supply values {voltage}V {current}A")
                    status["Power Supply"] = [f"{voltage}V {current}A", "green"]
                else:
                    status["Power Supply"] = not_initialized
            except Exception as e:
                logger.critical(f"Power Supply failed with {e}")

            # Data Values
            for key in data_labels:
                if "key" in data_labels[key]:
                    data_key = data_labels[key]["key"]
                    if data_key in self.data:
                        obj = self.data[data_key]
                        status[key] = data_labels[key]["validator"](obj, self.data)
                    else:
                        status[key] = not_initialized
                else:
                    status[key] = data_labels[key]["validator"](self.data)

            self.output.emit(status)
        except Exception as e:
            logger.critical(f"Exception in watcher: {e}")
            
        time.sleep(0.1)

class Watcher(QWidget):
    def __init__(self, kria_address: str, fetch_data) -> None:
        super().__init__()

        self.kria_address = kria_address
        self.fetch_data = fetch_data

        layout = QFormLayout()
        
        # Header
        label = QLabel("Live Outputs")
        font = label.font()
        font.setPointSizeF(font.pointSize() * 1.5)
        label.setFont(font)
        layout.addRow(label)
        
        # Text Fields
        self.text_fields = {}
        for text in pulled_labels:
            self.text_fields[text] = QLabel("Uninitialized")
            layout.addRow(QLabel(text), self.text_fields[text])
        for key in data_labels:
            self.text_fields[key] = QLabel("Uninitialized")
            layout.addRow(QLabel(key), self.text_fields[key])

        self.setLayout(layout)

        # Start Loop
        self.run_update()

    def update_text_fields(self, status: object) -> None:
        for key in status:
            if key not in self.text_fields:
                logger.critical(f"Invalid key in status: {key}")
                continue
            field = self.text_fields[key]
            field.setText(status[key][0])
            field.setStyleSheet(f"color: {status[key][1]};")

    def run_update(self) -> None:
        logger.debug("Running update.")
    
        if hasattr(self, "_thread"):
            self._thread.deleteLater()

        self._thread = WatcherThread(self.kria_address, self.fetch_data())
        # Parse Data
        self._thread.output.connect(self.update_text_fields)

        # Restart
        self._thread.finished.connect(self.run_update)
        self._thread.start()