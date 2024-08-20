from PyQt6.QtCore import Qt, QThread
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
        button = QPushButton("Next")
        button.clicked.connect(lambda: widget.finished.emit("Pressed"))
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
            
            layout.addWidget(image)

        # End Content
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)

        # Stretch
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
        button = QPushButton("Select")
        button.clicked.connect(lambda: widget.finished.emit(selector.currentText()))
        layout.addWidget(button)

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