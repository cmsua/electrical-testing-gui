from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton, QRadioButton, QComboBox

from objects import TestStep, TestWidget


# A test step that runs a thread in the background, without console output
# The step is done when the thread is finished. No value is returned
# from the thread
class ThreadStep(TestStep):
    
    # Message is the message shown to the user
    def __init__(self, name: str, message: str, auto_advance: bool=False, data_field: str=None) -> None:
        super().__init__(name, data_field)
        self._message = message
        self._auto_advance = auto_advance

    def create_thread(self, data) -> QThread:
        pass

    def create_widget(self, data: object) -> TestWidget:
        widget = TestWidget()
        layout = QVBoxLayout()

        label = QLabel(self._message)
        layout.addWidget(label)
        layout.addStretch()

        # Finish Button
        self.button = QPushButton("Task Not Finished. Please Wait.")
        self.button.clicked.connect(widget.advance.emit)
        self.button.setEnabled(False)
        layout.addWidget(self.button)

        # When thr thread exits
        self.finished_with_data = False
        self.finished_with_error = False
        def finished() -> None:
            # Crashed, don't allow auto advance and show an error
            if self.finished_with_error:
                self.button.setText("ERROR: Click to continue...")
                self.button.setEnabled(True)
            elif self._auto_advance:
                widget.advance.emit("Automatically advanced on thread finish")
            else:
                self.button.setText("Continue...")
                self.button.setEnabled(True)

        # When the thread exits with data, save it
        self._thread = self.create_thread(data)
        self._thread.finished.connect(finished)
        if hasattr(self._thread, "data"):
            self._thread.data.connect(widget.finished.emit)

        if hasattr(self._thread, "crash"):
            self._thread.crash.connect(widget.crashed.emit)

        self._thread.start()

        widget.setLayout(layout)
        return widget
    
class DynamicThread(QThread):
    data = pyqtSignal(object)
    crash = pyqtSignal(object)
    def __init__(self, method, data):
        super().__init__()
        self._method = method
        self._data = data
    
    def run(self):
        try:
            result = self._method(self._data)
            self.data.emit(result)
        except Exception as e:
            self.crash.emit(e)

# Dynamic Thread Step
# Used for threads that take actions dependant
# on data from previous steps
class DynamicThreadStep(ThreadStep):
    def __init__(self, name: str, message: str, method, auto_advance: bool=False, data_field: str=None) -> None:
        super().__init__(name, message, auto_advance, data_field)
        self._method = method

    def create_thread(self, data):
        return DynamicThread(self._method, data)