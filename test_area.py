from PyQt6.QtWidgets import QWidget, QSizePolicy, QFrame, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel

from misc_widgets import QHLine
from objects import TestFlow, TestStage, TestWidget, TestFinishedBehavior

import datetime
import logging
import log_utils

# This contains all the LEDs
class StatusWidget(QWidget):
    def __init__(self, flow: TestFlow) -> None:
        super().__init__()
        self._messages = {}
        layout = QVBoxLayout()

        # Header
        label = QLabel("Test Flow")
        font = label.font()
        font.setPointSizeF(font.pointSize() * 1.5)
        label.setFont(font)

        layout.addWidget(label)
        
        # Setup messages
        messages_layout = QFormLayout()
        
        # One column per stage
        for stage in TestStage:
            
            self._messages[stage] = []
            steps = flow.get_steps(stage)

            for step_index in range(len(steps)):
                step = steps[step_index]

                self._messages[stage].append(QLabel("Uninitialized"))
                messages_layout.addRow(QLabel(step.get_name()), self._messages[stage][step_index])
            
            messages_layout.addRow(QHLine())

        # Add LEDs
        messages_widget = QWidget()
        messages_widget.setLayout(messages_layout)
        layout.addWidget(messages_widget)
        layout.addStretch()

        # Final Touches
        self.setLayout(layout)

    def clear_messages(self):
        for stage in self._messages:
            for step in self._messages[stage]:
                step.setText("Uninitialized")
                step.setStyleSheet("")

    def set_message(self, stage: TestStage, stepIndex: int, message: str, color: str):
        self._messages[stage][stepIndex].setText(message)
        self._messages[stage][stepIndex].setStyleSheet(f"color: {color};")

    def set_messages(self, stage: TestStage, startIndex: int, message: str, color: str):
        for label_index in range(startIndex, len(self._messages[stage])):
            self._messages[stage][label_index].setText(message)
            self._messages[stage][label_index].setStyleSheet(f"color: {color};")

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
    def set_widget(self, widget: TestWidget) -> None:
        self._layout.replaceWidget(self._current_widget, widget)
        widget.displayed.emit()

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
        self._test_data = {}
        
        # Layout, Status, Interaction Area
        layout = QHBoxLayout()
        
        # Status Area
        status_frame = QFrame()

        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.addWidget(self._status)
        status_layout.addWidget(flow.get_watcher(lambda: self._test_data))

        status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_frame.setFrameShadow(QFrame.Shadow.Raised)
        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)

        # Main Area
        layout.addWidget(self._interaction)

        self.start_new_test()
        self.setLayout(layout)

        self.update_input_area("Starting Over")

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

    # A step crashed with an error
    # Process that, skip to cleanup
    def step_crashed(self, error):
        self.logger.critical(f"Stage {self._stage} step ID {self._index} crashed with error {error}")
        current_step = self._flow.get_steps(self._stage)[self._index]
        self.logger.critical(f"Step name: {current_step.get_name()}")

        # Save Debug Data
        if self._stage not in self._debug_data:
            self._debug_data[self._stage] = {}

        self._debug_data[self._stage][current_step.get_name()] = {
            "error": error,
            "time_finished": datetime.datetime.now()
        }

        self.handle_output_action({
            "color": "red",
            "message": f"Step crashed (See Console)",
            "behavior": TestFinishedBehavior.SKIP_TO_CLEANUP
        })

    # A step finished with data.
    # Process that data, then call the advance step function
    def step_finished(self, data):
        self.logger.info(f"Stage {self._stage} step ID {self._index} finished.")
        current_step = self._flow.get_steps(self._stage)[self._index]

        # Log Data
        self.logger.debug(f"Step {current_step.get_name()} returned data {data}. Assigning to {current_step.get_data_field()}")
        self._test_data[current_step.get_data_field()] = data

        # Save Debug Data
        if self._stage not in self._debug_data:
            self._debug_data[self._stage] = {}

        self._debug_data[self._stage][current_step.get_name()] = {
            "data": data,
            "time_finished": datetime.datetime.now()
        }

        # Update LEDs
        action = current_step.get_output_action(self._test_data, data)

        # Convert non-object actions
        if type(action) == bool:
            action = {
                "color": "green" if action else "red",
                "message": f"Passed" if action else "Failed",
                "behavior": TestFinishedBehavior.NEXT_STEP
            }
        elif type(action) == str:
            action = {
                "color": "green",
                "message": action,
                "behavior": TestFinishedBehavior.NEXT_STEP
            }
        elif "message" not in action and "color" not in action and "behavior" not in action:
            self.logger.critical(f"Invalid action reponse: {action}")
            status = {
                "color": "blue",
                "message": "See Console",
                "behavior": TestFinishedBehavior.NEXT_STEP
            }

        self.logger.info(f"Step {current_step.get_name()} returned action {action}")
        self.handle_output_action(action)
        
    # Handle an output action
    def handle_output_action(self, action):
        self._status.set_message(self._stage, self._index, action['message'], action["color"])

        # Handle behavior
        # Advance one step
        if action["behavior"] == TestFinishedBehavior.NEXT_STEP: 
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
        
        # Error, Skip to Cleanup
        if action["behavior"] == TestFinishedBehavior.SKIP_TO_CLEANUP:
            # Set the rest of this and possibly the next stage's leds
            if self._stage == TestStage.SETUP:
                # How?
                self.logger.critical("Errored in setup - how???")

                # Skip rest of phase
                steps = self._flow.get_steps(self._stage)
                for index in range(self._index, len(steps)):
                    self._status.set_messages(self._stage, index, "Skipped - Error", "red")

                # Skip all runtime    
                steps = self._flow.get_steps(TestStage.RUNTIME)
                for index in range(len(steps)):
                    self._status.set_messages(TestStage.RUNTIME, index, "Skipped - Error", "red")

                
                self.logger.warning("Skipping to Shutdown")
                self._stage = TestStage.SHUTDOWN
                self._index = 0
            # If errored in runtime, skip rest of runtime
            elif self._stage == TestStage.RUNTIME:

                steps = self._flow.get_steps(self._stage)
                for index in range(self._index, len(steps)):
                    self._status.set_messages(self._stage, index, "Skipped - Error", "red")


                self.logger.warning("Skipping to Shutdown")
                self._stage = TestStage.SHUTDOWN
                self._index = 0
            elif self._stage == TestStage.SHUTDOWN:
                # How???
                self.logger.critical("Errored in shutdown - how???")
                # Just give up
                self.start_new_test()

    # Call this method whenever self._stage or self._index is updated
    def update_input_area(self, reason: str) -> None:
        self.logger.info(f"Updating input with reason {reason}")

        if self._stage == TestStage.SETUP and self._index == 0:
            self.logger.info("Clearing LEDs as starting from first stage!")
            self._status.clear_messages()

        step = self._flow.get_steps(self._stage)[self._index]
        self.logger.info(f"Loading widget for step {step} from stage {self._stage} at index {self._index}")
        self.logger.debug(f"Loading widget with test data {self._test_data}")

        # Load New Widget
        widget = step.create_widget(self._test_data)
        widget.finished.connect(self.step_finished)
        widget.crashed.connect(self.step_crashed)
        widget.advance.connect(self.update_input_area)
        self._interaction.set_widget(widget)

        # Set Indicators to Blue
        self._status.set_message(self._stage, self._index, "Running...", "blue")