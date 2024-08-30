from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton, QRadioButton, QComboBox

from flows.objects import TestStep, TestWidget


# A step that shows a message
class DisplayStep(TestStep):

    # Message is the message shown to the user
    def __init__(self, name: str, message: str, image_path: str = None) -> None:
        super().__init__(name)
        self._message = message
        self._image_path = image_path

    def create_widget(self, data: object) -> TestWidget:
        widget = TestWidget()
        layout = QVBoxLayout()
        
        # Text
        text = QLabel(self._message)
        text.setWordWrap(True)
        layout.addWidget(text)

        # Image, if present
        if self._image_path:
            image = QLabel()
            image.setPixmap(QPixmap(self._image_path).scaled(786, 786, Qt.AspectRatioMode.KeepAspectRatio))
            
            layout.addWidget(image)

        # Stretch
        layout.addStretch()

        # Finished
        def finish():
            widget.finished.emit("Manually pressed")
            widget.advance.emit("Manually advanced")

        button = QPushButton("Next")
        button.clicked.connect(finish)
        layout.addWidget(button)

        # Wrapup
        widget.setLayout(layout)
        return widget
    

# A step that shows a message and asks for confirmation
class VerifyStep(TestStep):
    
    # Message is the message shown to the user
    def __init__(self, name: str, message: str, verifications: list, image_path: str = None) -> None:
        super().__init__(name)
        self._message = message
        self._image_path = image_path
        self._verifications = verifications

    def create_widget(self, data: object) -> TestWidget:
        widget = TestWidget()
        layout = QVBoxLayout()

        # Content
        content_layout = QHBoxLayout()
        
        # Left Section
        left_layout = QFormLayout()

        # Text
        text = QLabel(self._message)
        text.setWordWrap(True)
        left_layout.addRow(text)

        # Verifications
        for verification_text in self._verifications:
            label = QLabel(verification_text)
            
            # Buttons
            buttons_layout = QHBoxLayout()
            
            no_button = QRadioButton("No")
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
        # Image, if present
        if self._image_path:
            image = QLabel()
            image.setPixmap(QPixmap(self._image_path).scaled(786, 786, Qt.AspectRatioMode.KeepAspectRatio))
            
            content_layout.addWidget(image)

        # End Content
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)

        # Stretch
        layout.addStretch()

        # Finished
        def finish():
            widget.finished.emit("Manually pressed")
            widget.advance.emit("Manually advanced")

        button = QPushButton("Next")
        button.clicked.connect(finish)
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
        layout = QVBoxLayout()
        
        # Text, Selector
        text = QLabel(self._message)
        layout.addWidget(text)

        # Selector
        selector = QComboBox()
        selector.addItems(self._options)
        layout.addWidget(selector)

        # Stretch
        layout.addStretch()

        # Select Button
        def finish():
             widget.finished.emit(selector.currentText())
             widget.advance.emit("Manually advanced")
        button = QPushButton("Select")
        button.clicked.connect(finish)
        layout.addWidget(button)

        # Wrapup
        widget.setLayout(layout)
        return widget
    

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