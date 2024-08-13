from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel
from misc_widgets import QLed, QHLine

from flows import flows


# This contains all the LEDs
class StatusWidget(QFrame):
    def __init__(self, flow: flows.TestFlow) -> None:
        super().__init__()
        self._setup_leds = {}
        self._runtime_leds = {}
        self._shutdown_leds = {}

        layout = QFormLayout()

        # Header
        label = QLabel("Test Flow")
        font = label.font()
        font.setPointSizeF(font.pointSize() * 1.5)
        label.setFont(font)

        layout.addRow(label)
        
        # Setup LEDs
        for step in flow.get_setup_steps():
            # Create LEDs
            leds = [ QLed() for _ in range(step.get_outputs()) ]
            self._setup_leds[step.get_name()] = leds
            
            # Display LEDs
            line_layout = QHBoxLayout()
            for led in leds:
                line_layout.addWidget(led)
            line_widget = QWidget()
            line_widget.setLayout(line_layout)

            layout.addRow(QLabel(step.get_name()), line_widget)
            
        layout.addWidget(QHLine())
        for step in flow.get_runtime_steps():
            # Create LEDs
            leds = [ QLed() for _ in range(step.get_outputs()) ]
            self._runtime_leds[step.get_name()] = leds
            
            # Display LEDs
            line_layout = QHBoxLayout()
            for led in leds:
                line_layout.addWidget(led)
            line_widget = QWidget()
            line_widget.setLayout(line_layout)

            layout.addRow(QLabel(step.get_name()), line_widget)
            
        layout.addWidget(QHLine())
        for step in flow.get_shutdown_steps():
            # Create LEDs
            leds = [ QLed() for _ in range(step.get_outputs()) ]
            self._setup_leds[step.get_name()] = leds
            
            # Display LEDs
            line_layout = QHBoxLayout()
            for led in leds:
                line_layout.addWidget(led)
            line_widget = QWidget()
            line_widget.setLayout(line_layout)

            layout.addRow(QLabel(step.get_name()), line_widget)

        # Final Touches
        self.setLayout(layout)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

    def set_setup_led(self, name: str, color: str, index: int = 0):
        self._setup_leds[name][index].setState(color)

    def set_runtime_led(self, name: str, color: str, index: int = 0):
        self._runtime_leds[name][index].setState(color)

    def set_shutdown_led(self, name: str, color: str, index: int = 0):
        self._shutdown_leds[name][index].setState(color)

# The main test area, which handles everything
class TestArea(QWidget):

    def __init__(self, flow = flows.TestFlow) -> None:
        super().__init__()
        self._flow = flow
        self._status = StatusWidget(flow)
        self._phase = "setup"
        self._index = 0
        self._current_widget = QWidget()
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self._status)
        self.layout.addWidget(self._current_widget)
        self.layout.addStretch()

        self.update_input_area()
        self.setLayout(self.layout)

    # Internal method. Using the string in self._phase,
    # return the list of current steps
    def _current_steps_list(self) -> None:
        if self._phase == "setup":
            return self._flow.get_setup_steps()
        elif self._phase == "runtime":
            return self._flow.get_runtime_steps()
        elif self._phase == "shutdown":
            return self._flow.get_shutdown_steps()
        else:
            raise ValueError(f"{self._phase} is not a valid phase!")

    # A step finished with data. Process that data, then call the advance step function
    def step_finished(self, data):
        print(data)
        print(123)
        self.advance_step()

    # A step finished. Advance to the next one.
    def advance_step(self) -> None:
        # Get Current Steps
        current_steps = self._current_steps_list()
        
        # If we're finished with the current step
        if self._index + 1 == len(current_steps):
            self._index = 0
            # Advance to the next phase if it exists
            if self._phase == "setup":
                self._phase = "runtime"
            elif self._phase == "runtime":
                self._phase = "shutdown"
            elif self._phase == "shutdown":
                self._phase = "setup"
            else:
                raise ValueError(f"{self._phase} is not a valid phase!")
        # Otherwise, just advance the index
        else:
            self._index = self._index + 1
        
        self.update_input_area()

    # Call this method whenever self._phase or self._index is updated
    def update_input_area(self) -> None:
        steps = self._current_steps_list()
        widget = steps[self._index].create_widget(None)
        widget.finished.connect(self.step_finished)

        self.layout.replaceWidget(self._current_widget, widget)
        self._current_widget.deleteLater()
        self._current_widget = widget