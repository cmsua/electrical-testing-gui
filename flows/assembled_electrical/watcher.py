from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel, QTabWidget, QVBoxLayout
from PyQt6.QtGui import QFontDatabase

import logging
import os
import requests
import time

from .custom_steps import powersupply

logger = logging.getLogger("watcher")

labels_standalone = [
    "DAQ Client",
    "Kria", "Power Supply",
    
    # From Data
    "Power (Default)", "Power (Configured)",
    "I2C Checker (Default)", "I2C Checker (Configured)",

    "Pedestal Run Success",
    "Pedestal Run Corruption",
    "Pedestal Run Dead Channels",
    "Pedestal Run Noisy Channels",
]

labels_in_tabs = [
    "Pedestal Run Data",
    "Pedestal Scan Data",
    "vrefinv Data",
    "vrefnoinv Data"
]

labels = labels_in_tabs + labels_standalone

def check_status(status):
    if status == "PASS" or status == True:
        return "green"
    elif status == "FAIL" or status == False:
        return "red"
    else:
        return "blue"

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

class WatcherThread(QThread):
    output = pyqtSignal(object)
    def __init__(self, kria_address, data):
        super().__init__()

        self.kria_address = kria_address
        self.data = data

    def run(self):
        try:
            status = {}
            
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

                text = f"I2C: {i2c_response}\nDAQ: {daq_response}"
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
            except Exception as e:
                logger.critical(f"Power Supply failed with {e}")

            # Data Values

            # Power
            if "POWER:CONFIGURED" in self.data:
                # Color TBD
                # This will only be shown if default hasn't been ran
                status["Power (Default)"] = ["Not Ran!", "red"]

                status["Power (Configured)"] = [str(self.data["POWER:CONFIGURED"]), "green"]
            if "POWER:DEFAULT" in self.data:
                # Color TBD
                status["Power (Default)"] = [str(self.data["POWER:DEFAULT"]), "green"]


            # I2C Checker
            if "I2C_CHECKER:CONFIGURED" in self.data:
                # This will only be shown if default hasn't been ran
                status["I2C Checker (Default)"] = ["Not Ran!", "red"]

                value = self.data["I2C_CHECKER:CONFIGURED"]
                status["I2C Checker (Configured)"] = [value, check_status(value)]

            if "I2C_CHECKER:DEFAULT" in self.data:
                value = self.data["I2C_CHECKER:DEFAULT"]
                status["I2C Checker (Default)"] = [value, check_status(value)]

            # Pedestal Run
            if "PEDESTAL_RUN:TEST_SUCCESS" in self.data:
                value = self.data["PEDESTAL_RUN:TEST_SUCCESS"]
                status["Pedestal Run Success"] = [value, check_status(value)]

                value = self.data["PEDESTAL_RUN:CORRUPTION"]
                status["Pedestal Run Corruption"] = [value, check_status(value)]

                # 0 -> green, 1 -> yellow, 2+ -> red
                match_color = lambda num: "red" if num >= 2 else ("green" if num == 0 else "gold")
                
                value = self.data["PEDESTAL_RUN:NUMBER_CHANNELS_NOISE_AT0"]
                status["Pedestal Run Dead Channels"] = [value, match_color(value)]

                value = self.data["PEDESTAL_RUN:NUMBER_CHANNELS_NOISE_MORE2"]
                status["Pedestal Run Noisy Channels"] = [value, match_color(value)]

                value = "ID  | Noise   | Dead | Noisy\n"
                i = 0
                while True:
                    if f"PEDESTAL_RUN:{i}:0:NOISE" not in self.data:
                        break
                    value += f"{i}:0 | {self.data[f'PEDESTAL_RUN:{i}:0:NOISE']:.5f} | {self.data[f'PEDESTAL_RUN:{i}:0:NUMBER_CHANNELS_NOISE_AT0']}    | {self.data[f'PEDESTAL_RUN:{i}:0:NUMBER_CHANNELS_NOISE_MORE2']}\n"
                    value += f"{i}:1 | {self.data[f'PEDESTAL_RUN:{i}:1:NOISE']:.5f} | {self.data[f'PEDESTAL_RUN:{i}:1:NUMBER_CHANNELS_NOISE_AT0']}    | {self.data[f'PEDESTAL_RUN:{i}:1:NUMBER_CHANNELS_NOISE_MORE2']}\n"
                    i += 1

                status["Pedestal Run Data"] = [value, "blue"]

            # Pedestal Scan
            if "TRIM_INV:0:0:SLOPE_AVG" in self.data:
                value = "ID  | AVG     | RMS\n"
                i = 0
                while True:
                    if f"TRIM_INV:{i}:0:SLOPE_AVG" not in self.data:
                        break
                    value += f"{i}:0 | {self.data[f'TRIM_INV:{i}:0:SLOPE_AVG']:.5f} | {self.data[f'TRIM_INV:{i}:0:SLOPE_RMS']:.5f}\n"
                    value += f"{i}:1 | {self.data[f'TRIM_INV:{i}:1:SLOPE_AVG']:.5f} | {self.data[f'TRIM_INV:{i}:1:SLOPE_RMS']:.5f}\n"
                    i += 1

                status["Pedestal Scan Data"] = [value, "blue"]

            # vrefinv
            if "INV_VREF:0:0:SLOPE" in self.data:
                value = "ID  | SLOPE    | OFFSET    | BEST_VALUE\n"
                i = 0
                while True:
                    if f"INV_VREF:{i}:0:SLOPE" not in self.data:
                        break
                    value += f"{i}:0 | {self.data[f'INV_VREF:{i}:0:SLOPE']:.5f} | {self.data[f'INV_VREF:{i}:0:OFFSET']:.5f} | {self.data[f'INV_VREF:{i}:0:BEST_VALUE']}\n"
                    value += f"{i}:1 | {self.data[f'INV_VREF:{i}:1:SLOPE']:.5f} | {self.data[f'INV_VREF:{i}:1:OFFSET']:.5f} | {self.data[f'INV_VREF:{i}:0:BEST_VALUE']}\n"
                    i += 1

                status["vrefinv Data"] = [value, "blue"]

            # vrefnoinv
            if "NOINV_VREF:0:0:SLOPE" in self.data:
                value = "ID  | SLOPE    | OFFSET    | BEST_VALUE\n"
                i = 0
                while True:
                    if f"NOINV_VREF:{i}:0:SLOPE" not in self.data:
                        break
                    value += f"{i}:0 | {self.data[f'NOINV_VREF:{i}:0:SLOPE']:.5f} | {self.data[f'NOINV_VREF:{i}:0:OFFSET']:.5f} | {self.data[f'NOINV_VREF:{i}:0:BEST_VALUE']}\n"
                    value += f"{i}:1 | {self.data[f'NOINV_VREF:{i}:1:SLOPE']:.5f} | {self.data[f'NOINV_VREF:{i}:1:OFFSET']:.5f} | {self.data[f'INV_VREF:{i}:0:BEST_VALUE']}\n"
                    i += 1

                status["vrefnoinv Data"] = [value, "blue"]

            self.output.emit(status)
        except Exception as e:
            logger.critical(f"Exception in watcher: {e}")
            
        time.sleep(0.1)

class Watcher(QWidget):
    def __init__(self, kria_address: str, fetch_data) -> None:
        super().__init__()

        self.kria_address = kria_address
        self.fetch_data = fetch_data
        
        layout = QVBoxLayout()

        # Header
        label = QLabel("Live Outputs")
        font = label.font()
        font.setPointSizeF(font.pointSize() * 1.5)
        label.setFont(font)
        layout.addWidget(label)
        
        # Form Area
        form_layout = QFormLayout()
        # Text Fields
        self.text_fields = {}
        for text in labels_standalone:
            self.text_fields[text] = QLabel("Uninitialized")
            form_layout.addRow(QLabel(text), self.text_fields[text])

        # Bulk Data
        tabs = QTabWidget()
        for text in labels_in_tabs:
            self.text_fields[text] = QLabel("Uninitialized")
            self.text_fields[text].setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
            tabs.addTab(self.text_fields[text], text)
        
        form_layout.addRow(tabs)

        widget = QWidget()
        widget.setLayout(form_layout)
        layout.addWidget(widget)

        layout.addStretch()
        self.setLayout(layout)

        # Start Loop
        self.run_update()

    def update_text_fields(self, status: object) -> None:
        for key in labels:
            field = self.text_fields[key]
            if key not in status:
                logger.debug(f"Key not in status: {key}")
                field.setText("Uninitialized")
                field.setStyleSheet("")
                continue

            data = status[key]

            if isinstance(data, list):
                field.setText(str(data[0]))
                field.setStyleSheet(f"color: {data[1]};")
            else:
                field.setText(data)

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