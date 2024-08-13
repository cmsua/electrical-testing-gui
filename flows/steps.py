from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QFormLayout, QVBoxLayout, QLabel, QPushButton, QComboBox

from flows.objects import TestStep, TestWidget


# A step that shows a message and asks for confirmation
class VerifyStep(TestStep):
    
    # Message is the message shown to the user
    def __init__(self, name: str, message: str) -> None:
        super().__init__(name)
        self._message = message

    def create_widget(self, data: object) -> TestWidget:
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

    def create_widget(self, data: object) -> TestWidget:
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
    

# A test step that runs a thread in the background, without console output
# The step is done when the thread is finished. No value is returned
# from the thread
class ThreadStep(TestStep):
    
    # Message is the message shown to the user
    def __init__(self, name: str, message: str, thread: QThread) -> None:
        super().__init__(name)
        self._message = message
        self._thread = thread

    def create_widget(self, data: object) -> TestWidget:
        widget = TestWidget()
        layout = QVBoxLayout()

        label = QLabel(self._message)
        layout.addWidget(label)
        layout.addStretch()

        self.button = QPushButton("Task Not Finished. Please Wait.")
        self.button.clicked.connect(lambda: widget.finished.emit("Pressed"))
        self.button.setEnabled(False)
        layout.addWidget(self.button)

        def connected() -> None:
            self.button.setText("Continue...")
            self.button.setEnabled(True)

        self._thread.finished.connect(connected)
        self._thread.start()

        widget.setLayout(layout)
        return widget