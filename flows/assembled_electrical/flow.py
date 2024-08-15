from flows.steps import VerifyStep, SelectStep
from flows.objects import TestFlow, TestStage

from flows.assembled_electrical.powersupply import *
from flows.assembled_electrical.kria import *

from config import config


class AssembledHexaboardFlow(TestFlow):
    def __init__(self):
        self._setup_steps = [
            SelectStep("Select User", "Select User", config.get_users()),
            ConnectKriaStep(
                "Kria",
                config.get_kria_web_address(),
                0.05,
                "Ensure that the Kria is powered on and connected to the network. This may take a minute or two to load."
            ),
            ConnectPowerSupplyStep(
                "Power Supply",
                "power_supply",
                config.get_power_supply_address(),
                0.05,
                "Ensure that the power supply is on, and reading the following values:\n1.5V, 3.23A, No Channels On"
            ),
            VerifyStep(
                "Hexaboard Present",
                "Prepare an assembled hexaboard.",
                "static/assembled_electrical/hexaboard.jpg"
            ),
            VerifyStep(
                "Hexaboard In Position",
                "Place each hexaboard in the test stand. Note the orientation of the board in the stand, as the stand's clearance at the edges is not rotationally symnetric.",
                "static/assembled_electrical/hexaboard_in_riser.jpg"
            ),
            VerifyStep(
                "Power Cables",
                "Connect power cables to the hexaboard. Be careful to orient the connector board appropriately, as although it can be installed backwards, attempting to power the board while so will destroy it.",
                "static/assembled_electrical/power_cables.jpg"
            ),
            VerifyStep(
                "Trophy-Hexaboard",
                "Connect the hexaboard to a trophy. Some force may need applied. Support the test stand with your hand from below. The boards will connect with an audible snap.",
                "static/assembled_electrical/hexaboard_trophy.jpg"
            ),
            VerifyStep(
                "Trophy-Kria",
                "If not alreact connected, attach the trophy to the Kria. The boards will connect silently.",
                "static/assembled_electrical/kria_trophy.jpg"
            ),
            VerifyStep(
                "L3 Loopback",
                "Connect the L3 Loopback to the hexaboard. The board should not overlap with the trophy. When correctly, the hole in the L3 Loopback chip will be centered on a support pillar below.",
                "static/assembled_electrical/l3_loopback.jpg"
            )
        ]

        self._runtime_steps = [
            EnablePowerSupplyStep("Power Supply", "The power supply should be enabled. Ensure that Channel 1 is powered."),
            EnableKriaStep("Kria", config.get_kria_web_address(), "Ensure the central LEDs on the Kria have turned blue."),
            VerifyStep("Test", "Test")
        ]

        self._shutdown_steps = [
            DisableKriaStep("Kria", config.get_kria_web_address(), "Ensure the central LEDs on the Kria are no longer blue."),
            DisablePowerSupplyStep("Power Supply", "The power supply should be disabled. Ensure that no channels are powered."),
            VerifyStep("L3 Loopback", "Remove the L3 Loopback from the hexaboard"),
            VerifyStep("Trophy-Kria", "Disconnect the trophy from the Kria"),
            VerifyStep("Trophy-Hexaboard", "Disconnect the hexaboard from the trophy"),
            VerifyStep("Power Cables", "Connect power cables to the hexaboard"),
            VerifyStep("Sticker", "Pretend to place a sticker on the hexaboard"),
            VerifyStep("Remove Hexaboard", "Remove the hexaboard from the test stand")
        ]

    def get_steps(self, stage: TestStage) -> list[TestStep]:
        if stage == TestStage.SETUP:
            return self._setup_steps
        elif stage == TestStage.RUNTIME:
            return self._runtime_steps
        elif stage == TestStage.SHUTDOWN:
            return self._shutdown_steps