from flows.steps import *
from flows.flows import TestFlow
from config import config
from flows.steps import TestStep


class AssembledHexaboardFlow(TestFlow):
    def __init__(self):
        self._setup_steps = [
            #SelectStep("Select User", "Select User", config.get_users()),
            #VerifyKriaStep(),
            #VerifyPowerSupplyStep(),
            VerifyStep("Hexaboard Present", "Prepare an assembled hexaboard"),
            VerifyStep("Hexaboard In Position", "Place each hexaboard in the test stand"),
            VerifyStep("Power Cables", "Connect power cables to the hexaboard"),
            VerifyStep("Trophy-Hexaboard", "Connect the hexaboard to a trophy"),
            VerifyStep("Trophy-Kria", "Connect the trophy to the Kria"),
            VerifyStep("L3 Loopback", "Connect the L3 Loopback to the hexaboard")
        ]

        self._runtime_steps = [
            #EnablePowerStep()
            VerifyStep("Test", "Test")
        ]

        self._shutdown_steps = [
            #DisablePowerStep(),
            VerifyStep("L3 Loopback", "Remove the L3 Loopback from the hexaboard"),
            VerifyStep("Trophy-Kria", "Disconnect the trophy from the Kria"),
            VerifyStep("Trophy-Hexaboard", "Disconnect the hexaboard from the trophy")
        ]

    def get_setup_steps(self) -> list[TestStep]:
        return self._setup_steps

    def get_runtime_steps(self) -> list[TestStep]:
        return self._runtime_steps

    def get_shutdown_steps(self) -> list[TestStep]:
        return self._shutdown_steps