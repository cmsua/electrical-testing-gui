from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QRadioButton, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from objects import TestWidget, TestStep
from steps.input_steps import TextAreaStep
from .boards import boards

import logging

logger = logging.getLogger("scanner")


class CentralBarcodeStep(TextAreaStep):
    def __init__(self, name: str, message: str, data_field: str) -> None:
        super().__init__(name, message, data_field)

    def get_output_status(self, in_data, out_data) -> list[str]:
        return ['yellow' if out_data == '' else 'green']
    

class VerifyBoardStep(TestStep):
    def __init__(self, name: str, data_field: str):
        super().__init__(name, data_field)

    def create_widget(self, data: object) -> TestWidget:
        # Identify Board
        scanned_barcode = data["board_barcode"]
        found_board = boards["default"]
        found_board_key = "default"

        for key in boards:
            board = boards[key]
            if board["search_key"] in scanned_barcode:
                logger.info(f"Found board matching barcode: {board}, as {board['search_key']} in {scanned_barcode}")
                found_board_key = key
                found_board = board
                break
        
        if found_board is None:
            logger.critical("Could not find board!")


        widget = TestWidget()
        layout = QVBoxLayout()

        # Content
        content_layout = QHBoxLayout()
        
        # Left Section
        left_layout = QFormLayout()

        # Text
        text = QLabel(f"Board Identified: {found_board['name']}")
        text.setWordWrap(True)
        left_layout.addRow(text)

        # Verifications
        label = QLabel("Does your board look like the provided image?")
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        no_button = QRadioButton("No")
        no_button.setChecked(True)
        buttons_layout.addWidget(no_button)

        yes_button = QRadioButton("Yes")
        buttons_layout.addWidget(yes_button)
        
        buttons_layout.addStretch()

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        left_layout.addRow(label, buttons_widget)


        # End Left Section
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        content_layout.addWidget(left_widget)

        # Right Section
        # Image
        image = QLabel()
        image.setPixmap(QPixmap(found_board["image"]).scaled(786, 786, Qt.AspectRatioMode.KeepAspectRatio))
        content_layout.addWidget(image)

        # End Content
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)

        # Stretch
        layout.addStretch()

        # Finished
        def finish():
            if found_board_key == "default":
                widget.crashed.emit("Crashing, Invalid Board")
            elif not yes_button.isChecked():
                widget.crashed.emit("Board Mismatch Detected")
            else:
                widget.finished.emit(found_board_key)
            widget.advance.emit("Manually advanced")

        button = QPushButton("Invalid Board, Failing..." if found_board_key == "default" else "Next")
        button.clicked.connect(finish)
        layout.addWidget(button)

        # Focus Yes
        widget.displayed.connect(yes_button.setFocus)

        # Wrapup
        widget.setLayout(layout)
        return widget
    
class ScanHGCROCs(TestStep):
    def __init__(self, name: str, data_field: str):
        super().__init__(name, data_field)

    def create_widget(self, data: object) -> TestWidget:
        widget = TestWidget()
        layout = QVBoxLayout()
        
        # Board Info
        board = boards[data["board"]]

        # Text
        text = QLabel(f"This board should have {board['hgcrocs']} HGCROCs")
        layout.addWidget(text)

        # Verifications
        lines_layout = QFormLayout()
        lines = []
        for index in range(board['hgcrocs']):
            label = QLabel(f"HGCROC {index + 1}")
            lines.append(QLineEdit())
            lines_layout.addRow(label, lines[index])

        lines_widget = QWidget()
        lines_widget.setLayout(lines_layout)
        layout.addWidget(lines_widget)

        # Stretch
        layout.addStretch()

        # Finished
        def finish():
            result = [button.text() for button in lines]
            # Crash on missed barcode
            if not all(result):
                widget.crashed.emit(result)
            else:
                widget.finished.emit(result)
            widget.advance.emit("Manually advanced")

        button = QPushButton("Next")
        button.clicked.connect(finish)
        layout.addWidget(button)

        # Focus Text
        widget.displayed.connect(lines[0].setFocus)

        # Wrapup
        widget.setLayout(layout)
        return widget
    
    def get_output_status(self, in_data, out_data: list[str]) -> list[str]:
        return ["green" if all(out_data) else "yellow"]
