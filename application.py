from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

from status_widget import StatusBox
from multitester_widget import TestingArea
import sys

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Hexaboard Electrical Testing")
        layout = QVBoxLayout()

        # Add Header
        header = QLabel("Hexaboard Electrical Testing GUI")
        font = header.font()
        font.setPointSize(font.pointSize() * 2)
        header.setFont(font)

        layout.addWidget(header)
        layout.addWidget(TestingArea())

        # Status Box
        self.status_box = StatusBox()
        layout.addWidget(self.status_box)

        layout.addStretch()

        widget = QWidget()
        widget.setLayout(layout)

        self.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(widget)
        self.showFullScreen()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('dark')

    window = MainWindow()
    app.exec()