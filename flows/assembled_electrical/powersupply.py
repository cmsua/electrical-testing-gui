from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton

from flows.objects import TestStep, TestWidget
from flows.steps import VerifyStep

import time
import pyvisa


# Try and connect to the supply every X s.
class WaitForPowerSupply(QThread):
    supply = pyqtSignal(object)

    def __init__(self, address: str, delay: float) -> None:
        super().__init__()
        self._address = address
        self._delay = delay

    def run(self) -> None:
        rm = pyvisa.ResourceManager()
        while True:
            try:
                # Connect
                ps = rm.open_resource(self._address)
                ps.write_termination = "\n"
                ps.read_termination = "\n"

                # Turn Off            
                ps.write("OUTPut:TRACK 0")
                ps.write("OUTPut CH1,OFF")
                ps.write("OUTPut CH2,OFF")
                ps.write("OUTPut CH3,OFF")

                # Set Initial Values
                ps.write("CH1:VOLTage 1.5")
                ps.write("CH2:VOLTage 1.5")
                ps.write("CH1:CURRent 3.23")
                ps.write("CH2:CURRent 3.23")

                self.supply.emit(ps)
                return
            except:
                pass

            time.sleep(self._delay)


# Connect to a power supply task
class ConnectPowerSupplyStep(TestStep):
    def __init__(self, name: str, data_field: str, address: str, delay: float,
                 message: str) -> None:
        super().__init__(name, data_field)
        self._address = address
        self._delay = delay
        self._message = message

    def create_widget(self, data: object) -> TestWidget:
        widget = TestWidget()
        layout = QVBoxLayout()

        label = QLabel(self._message)
        layout.addWidget(label)
        layout.addStretch()

        self.button = QPushButton("Supply Not Connected. Please Wait.")
        self.button.setEnabled(False)
        layout.addWidget(self.button)

        self.thread = WaitForPowerSupply(self._address, self._delay)

        def supply_connected(ps) -> None:
            self.button.setText("Continue...")
            self.button.setEnabled(True)
            self.button.pressed.connect(lambda: widget.finished.emit(ps))
        self.thread.supply.connect(supply_connected)
        self.thread.start()

        widget.setLayout(layout)
        return widget
    

# Connect to a power supply task
class EnablePowerSupplyStep(VerifyStep):
    def __init__(self, name: str, message: str) -> None:
        super().__init__(name, message)

    def create_widget(self, data: object) -> TestWidget:
        data["power_supply"].write("OUTPut CH1,ON")
        return super().create_widget(data)
    
# Connect to a power supply task
class DisablePowerSupplyStep(VerifyStep):
    def __init__(self, name: str, message: str) -> None:
        super().__init__(name, message)

    def create_widget(self, data: object) -> TestWidget:
        data["power_supply"].write("OUTPut CH1,OFF")
        data["power_supply"].close()
        return super().create_widget(data)
    
