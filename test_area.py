from PyQt6.QtWidgets import QWidget, QSizePolicy, QFrame, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel
from misc_widgets import QLed

from flows.objects import TestFlow, TestStage
import datetime

import logging
import log_utils

# This contains all the LEDs
class StatusWidget(QFrame):
    def __init__(self, flow: TestFlow) -> None:
        super().__init__()
        self._leds = {}
        layout = QVBoxLayout()

        # Header
        label = QLabel("Test Flow")
        font = label.font()
        font.setPointSizeF(font.pointSize() * 1.5)
        label.setFont(font)

        layout.addWidget(label)
        
        # Setup LEDs
        leds_layout = QHBoxLayout()
        
        # One column per stage
        for stage in TestStage:
            stage_layout = QFormLayout()
            
            self._leds[stage] = []
            steps = flow.get_steps(stage)

            for step_index in range(len(steps)):
                step = steps[step_index]
                # Create LEDs
                leds = [QLed() for _ in range(step.get_output_count())]
                self._leds[stage].append(leds)
                
                # Display LEDs
                line_layout = QHBoxLayout()
                for led in leds:
                    line_layout.addWidget(led)
                line_widget = QWidget()
                line_widget.setLayout(line_layout)

                stage_layout.addRow(QLabel(step.get_name()), line_widget)
            
            # Add Stage
            stage_widget = QWidget()
            stage_widget.setLayout(stage_layout)
            leds_layout.addWidget(stage_widget)

        # Add LEDs
        leds_widget = QWidget()
        leds_widget.setLayout(leds_layout)
        layout.addWidget(leds_widget)
        layout.addStretch()

        # Final Touches
        self.setLayout(layout)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

    def set_all_leds(self, color: str):
        for stage in self._leds:
            for step in self._leds[stage]:
                for led in step:
                    led.setState(color)

    def set_led(self, stage: TestStage, stepIndex: int, index: int, color: str):
        self._leds[stage][stepIndex][index].setState(color)

    def set_leds(self, stage: TestStage, stepIndex: int, colors: str):
        step_leds = self._leds[stage][stepIndex]
        for i in range(len(step_leds)):
            step_leds[i].setState(colors[i])

# The interaction area, which has a main widget that constantly changes
class InteractionAreaWidget(QFrame):
    def __init__(self) -> None:
        super().__init__()

        # Set Main Widget as a blank
        self._current_widget = QWidget()

        self._layout = QVBoxLayout()

        # Header
        label = QLabel("Test Area")
        font = label.font()
        font.setPointSizeF(font.pointSize() * 1.5)
        label.setFont(font)
        self._layout.addWidget(label)
        
        # Add Generated Widget
        self._layout.addWidget(self._current_widget)

        # Finishing Touches
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLayout(self._layout)

    # Set the main widget and destroy the old
    def set_widget(self, widget: QWidget) -> None:
        self._layout.replaceWidget(self._current_widget, widget)
        self._current_widget.deleteLater()
        self._current_widget = widget

# The main test area, which handles everything
class TestArea(QWidget):
    def __init__(self, flow: TestFlow) -> None:
        super().__init__()
        # Logs
        self.logger = logging.getLogger("testing")
        self.logger.info("Created Test Area.")
        self.logger.info(f"Using flow {flow}")

        # Initial Variables
        self._flow = flow
        self._status = StatusWidget(flow)
        self._stage = TestStage.SETUP
        self._index = 0
        self._interaction = InteractionAreaWidget()
        
        # Layout, Status, Interaction Area
        layout = QHBoxLayout()
        layout.addWidget(self._status)
        layout.addWidget(self._interaction)

        self.start_new_test()
        self.setLayout(layout)

    # Start a new test!
    def start_new_test(self):
        # Wipe Logs
        self.logger.info("Starting New Test. Clearing Logs...")
        log_utils.logs = []
        self.logger.info("Starting New Test. Logs Cleared.")

        self._stage = TestStage.SETUP
        self._index = 0
        self._test_data = {}
        self._debug_data = {}
        
        self._status.set_all_leds("blue")
        self.update_input_area()

    # A step finished with data.
    # Process that data, then call the advance step function
    def step_finished(self, data):
        self.logger.info(f"Stage {self._stage} step ID {self._index} finished.")
        current_step = self._flow.get_steps(self._stage)[self._index]
        
        # Log Data
        self.logger.debug(f"Step {current_step.get_name()} returned data {data}. Assigning to {current_step.get_data_field()}")
        self._test_data[current_step.get_data_field()] = data

        # Update Colors
        status = current_step.get_output_status(data)
        self.logger.info(f"Step {current_step.get_name()} returned status {status}")
        self._status.set_leds(self._stage, self._index, status)

        # Save Debug Data
        if self._stage not in self._debug_data:
            self._debug_data[self._stage] = {}

        self._debug_data[self._stage][current_step.get_name()] = {
            "data": data,
            "time_finished": datetime.datetime.now()
        }

        self.advance_step()

    # A step finished. Advance to the next one.
    # If all tests are finished, start a new test
    def advance_step(self) -> None:
        self.logger.info(f"Advancing one step, from {self._stage} index {self._index}")
        # Get Current Steps
        current_steps = self._flow.get_steps(self._stage)
        
        # If we're finished with the current step
        if self._index + 1 == len(current_steps):
            self._index = 0
            # Advance to the next phase if it exists
            if self._stage == TestStage.SETUP:
                self._stage = TestStage.RUNTIME
            elif self._stage == TestStage.RUNTIME:
                self._stage = TestStage.SHUTDOWN
            elif self._stage == TestStage.SHUTDOWN:
                self.start_new_test()
                return
            else:
                raise ValueError(f"{self._stage} is not a valid phase!")
        # Otherwise, just advance the index
        else:
            self._index = self._index + 1
        
        self.update_input_area()

    # Call this method whenever self._stage or self._index is updated
    def update_input_area(self) -> None:
        step = self._flow.get_steps(self._stage)[self._index]
        self.logger.info(f"Loading widget for step {step} from stage {self._stage} at index {self._index}")
        self.logger.debug(f"Loading widget with test data {self._test_data}")

        # Load New Widget
        widget = step.create_widget(self._test_data)
        widget.finished.connect(self.step_finished)
        self._interaction.set_widget(widget)

        # Set Indicators to Orange
        self._status.set_leds(self._stage, self._index, ["yellow" for _ in range(step.get_output_count())])