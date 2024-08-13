from abc import ABC, abstractmethod
from flows import steps

# A test flow
class TestFlow(ABC):
    @abstractmethod
    def get_setup_steps(self) -> list[steps.TestStep]:
        pass
    
    @abstractmethod
    def get_runtime_steps(self) -> list[steps.TestStep]:
        pass

    @abstractmethod
    def get_shutdown_steps(self) -> list[steps.TestStep]:
        pass