from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

from config import config
from test_area import TestArea
from flows.assembled_electrical.flow import AssembledHexaboardFlow

import sys

import logging
import log_utils

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Hexaboard Electrical Testing")
        layout = QVBoxLayout()

        # Create Header
        # Add Title to header
        header = QLabel("Hexaboard Testing GUI")
        font = header.font()
        font.setPointSize(font.pointSize() * 3)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)

        # Add Institution Name
        header = QLabel(config.get_institution())
        font = header.font()
        font.setPointSize(int(font.pointSize() * 2))
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)

        # Add Testing Area
        layout.addWidget(TestArea(AssembledHexaboardFlow()))

        # Finalization
        widget = QWidget()
        widget.setLayout(layout)

        self.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(widget)
        self.showFullScreen()


if __name__ == "__main__":
    log_utils.setup_logging()

    app = QApplication(sys.argv)
    app.setStyle('dark')

    window = MainWindow()
    app.exec()