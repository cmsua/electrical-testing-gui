from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from abc import ABC, abstractmethod
from enum import Enum

# A widget representing one step of a test
class TestWidget(QWidget):
    # Emitted when the widget is displayed
    # Use to set focus
    displayed = pyqtSignal()
    
    # The test widget is presumed read-only after emitting finished or crashed
    # It will remain rendered until advance is passed
    finished = pyqtSignal(object)
    crashed = pyqtSignal(object)
    advance = pyqtSignal(object)

# Base class for a test step
class TestStep(ABC):
    @abstractmethod
    def __init__(self, name: str, data_field: str = None) -> None:
        self._name = name
        self._data_field = data_field
    
    def get_name(self) -> str:
        return self._name
    
    # The field the data output should be placed under
    def get_data_field(self) -> str:
        return self._data_field
    
    # How many output LEDs there are
    def get_output_count(self) -> int:
        return 1
    
    # Given data returned by the widget, returns an array with
    # length get_output_count() whose values are colors
    def get_output_status(self, in_data, out_data) -> list[str]:
        return ["green"]

    @abstractmethod
    def create_widget(self, data: object) -> TestWidget:
        pass


class TestStage(Enum):
    SETUP = 0
    RUNTIME = 1
    SHUTDOWN = 2
    

# A test flow
class TestFlow(ABC):
    @abstractmethod
    def get_steps(self, flow: TestStage) -> list[TestStep]:
        pass