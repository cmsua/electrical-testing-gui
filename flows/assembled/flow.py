from flows.steps import VerifyStep, SelectStep
from flows.objects import TestFlow, TestStage

from flows.assembled.powersupply import *
from flows.assembled.kria import *

from config import config


class AssembledHexaboardFlow(TestFlow):
    def __init__(self):
        self._setup_steps = [
            SelectStep("Select User", "Select User", config.get_users()),
            ConnectKriaStep("Kria", config.get_kria_web_address(), 0.05, "Ensure that the Kria is powered on. This may take a minute or two to load."),
            ConnectPowerSupplyStep("Power Supply", "power_supply", config.get_power_supply_address(), 0.05, "Ensure that the power supply is on, and reading the following values:\n1.5V, 3.23A, No Channels On"),
            VerifyStep("Hexaboard Present", "Prepare an assembled hexaboard"),
            VerifyStep("Hexaboard In Position", "Place each hexaboard in the test stand"),
            VerifyStep("Power Cables", "Connect power cables to the hexaboard"),
            VerifyStep("Trophy-Hexaboard", "Connect the hexaboard to a trophy"),
            VerifyStep("Trophy-Kria", "Connect the trophy to the Kria"),
            VerifyStep("L3 Loopback", "Connect the L3 Loopback to the hexaboard")
        ]

        self._runtime_steps = [
            EnableKriaStep("Kria", config.get_kria_web_address(), "Ensure the central LEDs on the Kria have turned blue."),
            EnablePowerSupplyStep("Power Supply", "The power supply should be enabled. Ensure that Channel 1 is powered."),
            VerifyStep("Test", "Test")
        ]

        self._shutdown_steps = [
            DisableKriaStep("Kria", config.get_kria_web_address(), "Ensure the central LEDs on the Kria are no longer blue."),
            DisablePowerSupplyStep("Power Supply", "The power supply should be disabled. Ensure that no channels are powered."),
            VerifyStep("L3 Loopback", "Remove the L3 Loopback from the hexaboard"),
            VerifyStep("Trophy-Kria", "Disconnect the trophy from the Kria"),
            VerifyStep("Trophy-Hexaboard", "Disconnect the hexaboard from the trophy")
        ]

    def get_steps(self, stage: TestStage) -> list[TestStep]:
        if stage == TestStage.SETUP:
            return self._setup_steps
        elif stage == TestStage.RUNTIME:
            return self._runtime_steps
        elif stage == TestStage.SHUTDOWN:
            return self._shutdown_steps