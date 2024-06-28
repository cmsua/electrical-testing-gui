from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel
from misc_widgets import Led
from config import config
from status import query_hexacontroller_status

class StatusBox(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()

        # Label
        label = QLabel("Hexacontroller Status")
        font = label.font()
        font.setPointSize(font.pointSize() * 1.5)
        label.setFont(font)
        layout.addWidget(label)
        
        # Data Section
        dataLayout = QHBoxLayout()
        
        hexacontrollers = config.getHexacontrollers()
        self.status_columns = [ StatusColumn(controller) for controller in hexacontrollers ]
        for column in self.status_columns:
            dataLayout.addWidget(column)
        
        dataLayout.addStretch()

        dataWidget = QWidget()
        dataWidget.setLayout(dataLayout)
        layout.addWidget(dataWidget)

        layout.addStretch()

        self.setLayout(layout)

class StatusColumn(QWidget):
    def __init__(self, hexacontrollerId: str) -> None:
        super().__init__()
        self.id = hexacontrollerId
        layout = QGridLayout()

        # Title
        title = QLabel(config.getHexacontrollerName(self.id))
        font = title.font()
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title, 0, 0, 1, 2)

        # Add Lights, Labels
        labels = [ "Connected", "Zynq", "I2C Server", "DAQ Server" ]
        self.leds = []
        for i in range(len(labels)):
            self.leds.append(Led())
            layout.addWidget(self.leds[i], i + 1, 1)

            label = QLabel(labels[i])
            layout.addWidget(label, i + 1, 0)

        # Set initial data
        self.updateStatus()
        self.startTimer(1000)

        self.setLayout(layout)

    def timerEvent(self, event) -> None:
        self.updateStatus()

    # Update leds based on hexacontroller status
    def updateStatus(self) -> None:
        status = query_hexacontroller_status(self.id)
        
        # Helper method. Red = false, Green = true, Blue = none
        def colorFromStatus(status: str) -> str:
            if status == None:
                return "blue"
            elif status:
                return "green"
            else:
                return "red"
            
        valueOrder = [ "network", "zynq", "i2cserver", "daqserver" ]
        for i in range(len(valueOrder)):
            self.leds[i].setState(colorFromStatus(status[valueOrder[i]]))