from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel

import requests
import logging

import time

logger = logging.getLogger("Watcher")

labels = ["Local Puller",
          "Kria", "Power Supply",
          "Test Status",
          "Power (Normal)", "Power (Configured)",
          "I2C Checker Status",
          "Pedestal Run 0-0 Status",
          "Pedestal Run 0-1 Status",
          "Pedestal Run 1-0 Status",
          "Pedestal Run 1-1 Status",
          "Pedestal Run 2-0 Status",
          "Pedestal Run 2-1 Status",
          "Pedestal Run Dead Channels",
          "Pedestal Run Noisy Channels",
          "Pedestal Run Corruption"]

redis_labels = ["Test Status",
          "Power (Normal)", "Power (Configured)",
          "I2C Checker Status",
          "Pedestal Run 0-0 Status",
          "Pedestal Run 0-1 Status",
          "Pedestal Run 1-0 Status",
          "Pedestal Run 1-1 Status",
          "Pedestal Run 2-0 Status",
          "Pedestal Run 2-1 Status",
          "Pedestal Run Dead Channels",
          "Pedestal Run Noisy Channels",
          "Pedestal Run Corruption"]


class WatcherThread(QThread):
    output = pyqtSignal(object)
    def __init__(self, kria_address, data):
        super().__init__()

        self.kria_address = kria_address
        self.data = data

    def run(self):
        status = {}
        not_initialized = ["Not Initialized", "yellow"]
        
        # Check Kria Services
        try:
            daq_response = requests.get(f"{self.kria_address}/daq", timeout=0.1).json()["text"].split("Active: ")[1].split(" since")[0]
            logger.debug(f"Recieved daq-server status {daq_response}")

            i2c_response = requests.get(f"{self.kria_address}/daq", timeout=0.1).json()["text"].split("Active: ")[1].split(" since")[0]
            logger.debug(f"Recieved i2c-server status {i2c_response}")

            text = f"I2C: {i2c_response}, DAQ: {daq_response}"
            color = "green" if i2c_response == "active (running)" and daq_response == "active (running)" else "red"
            status["Kria"] = [text, color]
        except requests.exceptions.Timeout as exception:
            logger.critical(f"Request timed out: {exception}")
            status["Kria"] = ["Timed Out", "red"]

        # Check Power Supply
        try:
            if "power_supply" in self.data:                
                voltage = float(self.data["power_supply"].query("MEASure:VOLTage? CH1")),
                current = float(self.data["power_supply"].query("MEASure:CURRent? CH1"))
                logger.debug(f"Read Power Supply values {voltage}V {current}A")
                status["Power Supply"] = [f"{voltage}V {current}A", "green"]
            else:
                status["Power Supply"] = not_initialized
        except Exception as e:
            logger.critical(f"Power Supply failed with {e}")

        # Redis Values
        if "redis" in self.data:
            redis = self.data["redis"]
            redis_data = redis.client.hgetall(redis.key)

            # Status
            if "TEST_SUCCESS" in redis_data:
                value = redis_data["TEST_SUCCESS"]
                color = "green" if value == "PASS" else "red"
                logger.debug(f"Read test status {value} with status {status}")
                status["Test Status"] = [value, color]
            else:
                status["Test Status"] = not_initialized

            # Power
            if "POWER:DEFAULT" in redis_data:
                value = redis_data["POWER:DEFAULT"]
                color = "yellow" # I saw POWER:DEFAULT:PASSED in an earlier model - don't want config values here
                logger.debug(f"Read default power {value} with status {status}")
                status["Power (Normal)"] = [value, color]
            else:
                status["Test Status"] = not_initialized

            if "POWER:CONFIGURED" in redis_data:
                value = redis_data["POWER:CONFIGURED"]
                color = "yellow" # I saw POWER:DEFAULT:PASSED in an earlier model - don't want config values here
                logger.debug(f"Read configured power {value} with status {status}")
                status["Power (Configured)"] = [value, color]
            else:
                status["Test Status"] = not_initialized

        else:
            logger.debug("Tests not started, skipping...")
            for text in redis_labels:
                status[text] = not_initialized

        self.output.emit(status)
        time.sleep(2)

class Watcher(QWidget):
    def __init__(self, kria_address: str, fetch_data) -> None:
        super().__init__()

        self.kria_address = kria_address
        self.fetch_data = fetch_data

        # Header Already Provided
        layout = QFormLayout()
        
        self.text_fields = {}
        for text in labels:
            self.text_fields[text] = QLabel("Uninitialized")
            layout.addRow(QLabel(text), self.text_fields[text])

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
        logger.info("Running update.")
    
        if hasattr(self, "_thread"):
            self._thread.deleteLater()

        self._thread = WatcherThread(self.kria_address, self.fetch_data())
        # Parse Data
        self._thread.output.connect(self.update_text_fields)

        # Restart
        self._thread.finished.connect(self.run_update)
        self._thread.start()