from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QTabWidget, QPlainTextEdit
from PyQt6.QtGui import QPixmap

from objects import TestStep, TestWidget

import glob
import traceback
import os

# A test step that runs a thread in the background, without console output
# The step is done when the thread is finished. No value is returned
# from the thread
class ThreadStep(TestStep):
    
    # Message is the message shown to the user
    def __init__(self, name: str, message: str, auto_advance: bool=False, data_field: str=None, timeout: int=0, image_fetcher=None) -> None:
        super().__init__(name, data_field)
        self._message = message
        self._auto_advance = auto_advance
        self._timeout = timeout
        self._image_fetcher = image_fetcher

    def create_thread(self, data) -> QThread:
        pass

    def create_widget(self, data: object) -> TestWidget:
        widget = TestWidget()
        layout = QVBoxLayout()

        # Label and Message
        label = QLabel(self._message)
        layout.addWidget(label)

        result_widget = QWidget()
        layout.addWidget(result_widget)

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

        # Focus Finish Button
        widget.displayed.connect(self.button.setFocus)

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
                # Finished normally, show files
                if self._image_fetcher is not None:
                    tabs = QTabWidget()
                    for file in sorted(self._image_fetcher(data)):
                        if file.endswith(".png"):
                            file_widget = QLabel()
                            file_widget.setPixmap(QPixmap(file).scaled(786, 786, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        elif file.endswith(".txt") or file.endswith(".yaml"):
                            with open(file, "r") as file_obj:
                                file_widget = QPlainTextEdit(file_obj.read())
                                file_widget.setEnabled(False)
                        else:
                            file_widget = QLabel(f"Invalid File Extension for {file}")
                        tabs.addTab(file_widget, os.path.basename(file))
                    result_layout = QVBoxLayout()
                    result_layout.addWidget(tabs)
                    result_widget.setLayout(result_layout)

                # Continue Button
                self.button.setText("Continue...")
                self.button.setEnabled(True)
                self.button.setFocus()

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
            self.crash.emit(str(e) + ",\n" + traceback.format_exc())

# Dynamic Thread Step
# Used for threads that take actions dependant
# on data from previous steps
class DynamicThreadStep(ThreadStep):
    def __init__(self, name: str, message: str, method, auto_advance: bool=False, data_field: str=None, timeout: int=0, action=None, image_fetcher=None) -> None:
        super().__init__(name, message, auto_advance, data_field, timeout, image_fetcher)
        self._method = method
        self._action = action

    def create_thread(self, data):
        return DynamicThread(self._method, data)
    
    def get_output_action(self, in_data, out_data):
        if (self._action):
            return self._action(in_data, out_data)
        return super().get_output_action(in_data, out_data)