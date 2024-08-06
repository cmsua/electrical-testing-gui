from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QTextCursor, QPalette, QPixmap, QPainter
from PyQt6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit, QLabel, QPushButton
from misc_widgets import ScannerLineEdit

from config import config

import multitester

import os
import logging
import re
from datetime import datetime
from functools import partial

from ansi2html import Ansi2HTMLConverter
console_color = re.compile(r"\[\d{,3}(;\d{,3}){4}m")
converter = Ansi2HTMLConverter()


class TestingArea(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout()

        # Label
        label = QLabel("Testing Data")
        font = label.font()
        font.setPointSize(int(font.pointSize() * 1.5))
        label.setFont(font)
        layout.addWidget(label)
        
        # Data Section, Tabs below
        dataLayout = QHBoxLayout()
        logTabs = QTabWidget()
        imageTabs = QTabWidget()
        
        hexacontrollers = config.getHexacontrollers()
        self.textAreas = {}
        self.imageLabels = {}
        for controller in hexacontrollers:
            # Create Image
            label = QLabel("Plot will go here.")
            label.setMaximumWidth(1536)
            label.setMinimumWidth(1536)
            label.setMaximumHeight(1024)
            self.imageLabels[controller] = label
            imageTabs.addTab(label, config.getHexacontrollerName(controller))

            # Create log text area
            textArea = QTextEdit()
            textArea.setReadOnly(True)
            pallete = textArea.palette()
            pallete.setColor(QPalette.ColorRole.Base, 0)
            textArea.setPalette(pallete)

            self.textAreas[controller] = textArea
            logTabs.addTab(textArea, config.getHexacontrollerName(controller))

            # On line recieve
            def insertLine(controller: str, line: str) -> None:
                self.textAreas[controller].moveCursor(QTextCursor.MoveOperation.End)
                self.textAreas[controller].insertHtml(line)
                self.textAreas[controller].moveCursor(QTextCursor.MoveOperation.End)

            # On image recieve
            def setImage(controller, image: QPixmap | None) -> None:
                label = self.imageLabels[controller]
                if image is None:
                    label.setText("Plot will go here.")
                else:
                    image = image.scaled(label.maximumWidth(), label.maximumHeight(), Qt.AspectRatioMode.KeepAspectRatio)
                    label.setPixmap(image)
            column = InputColumn(controller)
            column.line.connect(partial(insertLine, controller))
            column.clear.connect(textArea.clear)
            column.image.connect(partial(setImage, controller))
            dataLayout.addWidget(column)
        
        dataLayout.addStretch()
        dataWidget = QWidget()
        dataWidget.setLayout(dataLayout)
        layout.addWidget(dataWidget)

        layout.addWidget(logTabs)
        layout.addWidget(imageTabs)

        # Finish Setup

        layout.addStretch()

        self.setLayout(layout)


# A column that asks for all applicable inputs
class InputColumn(QWidget):
    line = pyqtSignal(str)
    image = pyqtSignal(object)
    clear = pyqtSignal()

    def __init__(self, hexacontrollerId: str) -> None:
        super().__init__()
        self.id = hexacontrollerId
        layout = QFormLayout()

        # Title
        title = QLabel(config.getHexacontrollerName(self.id))
        font = title.font()
        font.setBold(True)
        title.setFont(font)
        layout.addRow(title)

        # Add Labels
        self.boardField = ScannerLineEdit()
        self.boardField.setMaxLength(15)
        layout.addRow("Board ID", self.boardField)

        self.hgroc0Field = ScannerLineEdit()
        self.hgroc0Field.setMaxLength(15)
        layout.addRow("HGROC 0", self.hgroc0Field)

        self.hgroc1Field = ScannerLineEdit()
        self.hgroc1Field.setMaxLength(15)
        layout.addRow("HGROC 1", self.hgroc1Field)

        self.hgroc2Field = ScannerLineEdit()
        self.hgroc2Field.setMaxLength(15)
        layout.addRow("HGROC 2", self.hgroc2Field)

        # Start Tests
        self.button = QPushButton("Start Test")
        self.button.clicked.connect(self.start_test)
        layout.addRow(self.button)

        # Indicator
        self.status = QLabel("Tests Not Running")
        self.status.setStyleSheet("background-color: grey; color: white; border-radius: 5px; padding: 5px")
        layout.addRow(self.status)

        self.setLayout(layout)

    def start_test(self) -> None:
        logger = logging.getLogger(self.id)
        self.timestamp = datetime.now().isoformat()
        logger.info("Starting test for " + self.id + " at " + self.timestamp)
        
        # Disable inputs till test is concluded
        self.boardField.setEnabled(False)
        self.hgroc0Field.setEnabled(False)
        self.hgroc1Field.setEnabled(False)
        self.hgroc2Field.setEnabled(False)

        # Set Running Indicator
        self.status.setText("Tests In Progress")
        self.status.setStyleSheet("background-color: blue; color: white; border-radius: 5px; padding: 5px")

        # Disable Input
        self.button.setText("Tests In Progress...")
        self.button.setEnabled(False)

        multitester.setup_test(self.id, self.boardField.text(), self.hgroc0Field.text(), self.hgroc1Field.text(), self.hgroc2Field.text(), self.timestamp)

        # Start Tests
        self.clear.emit()
        self.image.emit(None)
        self.test_thread = multitester.TestThread(self.id, self.boardField.text(), self.timestamp)
        self.test_thread.exit.connect(self.finish_test)
        self.test_thread.line.connect(self.new_line)
        self.test_thread.start()


    # Called each time the test script prints a new line
    def new_line(self, line: str) -> None:
        self.line.emit(line)
        
    # Re-Enable Tests after finished
    def finish_test(self, exit_code: int) -> None:
        # Re-enable inputs, clear inputs
        self.boardField.setEnabled(True)
        self.boardField.clear()

        self.hgroc0Field.setEnabled(True)
        self.hgroc0Field.clear()

        self.hgroc1Field.setEnabled(True)
        self.hgroc1Field.clear()

        self.hgroc2Field.setEnabled(True)
        self.hgroc2Field.clear()

        # Re-enable start button
        self.button.setText("Start Test")
        self.button.setEnabled(True)

        # Set status based on exit code
        if exit_code == 0:
            self.status.setText("Tests Passsed")
            self.status.setStyleSheet("background-color: green; color: white; border-radius: 5px; padding: 5px")
        else:
            self.status.setText(f"Tests Failed (Exit Code {exit_code}), Check Logs")
            self.status.setStyleSheet("background-color: red; color: white; border-radius: 5px; padding: 5px")


        # Emit images
        pedestal_run_dir = f"{config.getOutputDir()}/{self.boardField.text()}-{self.timestamp}/pedestal_run"
        try:
            # Find latest
            files = os.listdir(pedestal_run_dir)

            times = [os.stat(f"{pedestal_run_dir}/{file}").st_mtime for file in files]
            latest = files[max(range(len(times)), key=times.__getitem__)]

            # Load pixmaps
            images = [
                QPixmap(f"{pedestal_run_dir}/{latest}/noise_vs_channel_chip0.png"),
                QPixmap(f"{pedestal_run_dir}/{latest}/noise_vs_channel_chip1.png"),
                QPixmap(f"{pedestal_run_dir}/{latest}/noise_vs_channel_chip2.png")
            ]

            # Stitch together
            stitched = QPixmap(sum([image.width() for image in images]), max([image.height() for image in images]))
            painter = QPainter(stitched)
            painter.setBackground(0)
            painter.setPen(0)
            x_pos = 0
            for image in images:
                painter.drawPixmap(x_pos, 0, image.width(), image.height(), image)
                x_pos = x_pos + image.width()

            # Exit
            painter.end()
            self.image.emit(stitched)
        except Exception as e:
            print(e)
