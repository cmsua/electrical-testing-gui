from abc import ABC, abstractmethod

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QLabel, QPushButton, QComboBox

# The list of all outputs from previous tests to date
class TestRollingOptions(ABC):
    pass


# A widget representing one step of a test
class TestWidget(QWidget):
    finished = pyqtSignal(str)

# Base class for a test step
class TestStep(ABC):
    @abstractmethod
    def __init__(self, name: str) -> None:
        self._name = name
    
    def get_name(self) -> str:
        return self._name
    
    def get_outputs(self) -> int:
        return 1

    @abstractmethod
    def create_widget(self, options: TestRollingOptions) -> TestWidget:
        pass
    

# A step that shows a message and asks for confirmation
class VerifyStep(TestStep):
    
    # Message is the message shown to the user
    def __init__(self, name: str, message: str) -> None:
        super().__init__(name)
        self._message = message

    def create_widget(self, options: TestRollingOptions) -> TestWidget:
        widget = TestWidget()
        layout = QVBoxLayout()
        
        # Text
        text = QLabel(self._message)
        layout.addWidget(text)
        layout.addStretch()

        # Finished
        button = QPushButton("Next")
        button.clicked.connect(lambda: widget.finished.emit("Pressed"))
        layout.addWidget(button)

        # Wrapup
        widget.setLayout(layout)
        return widget
    

# A step that shows a dropdown with options and asks for one
class SelectStep(TestStep):
    def __init__(self, name: str, message: str, options: list[str]) -> None:
        super().__init__(name)
        self._message = message
        self._options = options

    def create_widget(self, options: TestRollingOptions) -> TestWidget:
        widget = TestWidget()
        layout = QFormLayout()
        
        # Text
        text = QLabel(self._message)
        layout.addRow(text)

        # Dropdown
        selector = QComboBox()
        selector.addItems(self._options)

        button = QPushButton("Select")
        button.clicked.connect(lambda: widget.finished.emit(selector.currentText()))
        layout.addRow(selector, button)

        # Wrapup
        widget.setLayout(layout)
        return widget