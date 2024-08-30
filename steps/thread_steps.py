from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton

from objects import TestStep, TestWidget


# A test step that runs a thread in the background, without console output
# The step is done when the thread is finished. No value is returned
# from the thread
class ThreadStep(TestStep):
    
    # Message is the message shown to the user
    def __init__(self, name: str, message: str, auto_advance: bool=False, data_field: str=None, timeout: int=0) -> None:
        super().__init__(name, data_field)
        self._message = message
        self._auto_advance = auto_advance
        self._timeout = timeout

    def create_thread(self, data) -> QThread:
        pass

    def create_widget(self, data: object) -> TestWidget:
        widget = TestWidget()
        layout = QVBoxLayout()

        label = QLabel(self._message)
        layout.addWidget(label)
        layout.addStretch()

        # Tiemout Label
        if self._timeout > 0:
            self._time = self._timeout
            self.timeout_label = QLabel(f"Timeout in {self._time}s")
            layout.addWidget(self.timeout_label)


        # Abort Button
        self.abort_button = QPushButton("Abort Thread")

        # Abort Thread Logic
        def abort_thread():
            # Kill Thread
            self._thread.terminate()

            # Kill Timeout
            if self._timeout > 0:
                self._timer.stop()

            # Emit data
            widget.crashed.emit("Thread Manually Killed")
            self.button.setText("ERROR: Thread Aborted. Click to continue...")
            self.button.setEnabled(True)
        self.abort_button.clicked.connect(abort_thread)
        layout.addWidget(self.abort_button)

        # Finish Button
        self.button = QPushButton("Task Not Finished. Please Wait.")
        self.button.clicked.connect(widget.advance.emit)
        self.button.setEnabled(False)
        layout.addWidget(self.button)

        # When thr thread exits
        self.finished_with_data = False
        self.finished_with_error = False
        def finished() -> None:
            self.abort_button.setEnabled(False)

            # Kill Timer
            if self._timeout > 0:
                self._timer.stop()
                self.timeout_label.setText("Thread Finished")
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
            def handle_data(data):
                self.finished_with_data = True
                widget.finished.emit(data)
            self._thread.data.connect(handle_data)

        if hasattr(self._thread, "crash"):
            def handle_error(data):
                self.finished_with_error = True
                widget.crashed.emit(data)
            self._thread.crash.connect(handle_error)

        # Start Thread
        self._thread.start()

        # Start Timeout
        if self._timeout > 0:
            def tick_clock():
                self._time = self._time - 1
                self.timeout_label.setText(f"Timeout in {self._time}s")
                if self._time == 0:
                    # Stop thread
                    self._timer.stop()
                    self._thread.terminate()
                    # Disable auto advance
                    self.finished_with_error = True 

                    # Emit crash
                    widget.crashed.emit("Thread timed out!")

                    # Disable abort, etc
                    self.abort_button.setEnabled(False)
                    self.button.setText("ERROR: Thread killed due to timeout")
                    self.button.setEnabled(True)
            
            self._timer = QTimer()
            self._timer.timeout.connect(tick_clock)
            self._timer.start(1000)

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
    def __init__(self, name: str, message: str, method, auto_advance: bool=False, data_field: str=None, timeout: int=0) -> None:
        super().__init__(name, message, auto_advance, data_field, timeout)
        self._method = method

    def create_thread(self, data):
        return DynamicThread(self._method, data)