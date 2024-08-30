from steps.input_steps import DisplayStep, VerifyStep, SelectStep
from steps.thread_steps import DynamicThreadStep

from objects import TestFlow, TestStage, TestStep

from flows.assembled_electrical.powersupply import *
from flows.assembled_electrical.kria import *
from flows.assembled_electrical.redis import *
from flows.assembled_electrical.tests import *
from flows.assembled_electrical.cleanup import cleanup

from functools import partial

from config import config

import os

# Required for unpack
os.environ["PATH"] = os.environ["PATH"] + ":" + os.path.abspath(os.path.join(config.get_hexactrl_software_dir(), "bin"))

class AssembledHexaboardFlow(TestFlow):
    def __init__(self):
        self._setup_steps = [
            DisplayStep("ESD", "Ensure you are wearing an ESD strap"),
            SelectStep("Select User", "Select User", config.get_users()),
            DynamicThreadStep(
                "Kria",
                "Ensure that the Kria is powered on and connected to the network. This may take a minute or two to load.",
                partial(wait_for_kria, config.get_kria_web_address(), 0.05),
                True
            ),
            DynamicThreadStep(
                "Power Supply",
                "Ensure that the power supply is on, and reading the following values:\n1.5V, 3.23A, No Channels On",
                partial(wait_for_power_supply, config.get_power_supply_address(), 0.05),
                False,
                "power_supply"
            ),
            DisplayStep(
                "Hexaboard Present",
                "Prepare an assembled hexaboard.",
                "static/assembled_electrical/hexaboard.jpg"
            ),
            DisplayStep(
                "Hexaboard In Position",
                "Place each hexaboard in the test stand. Note the orientation of the board in the stand, as the stand's clearance at the edges is not rotationally symnetric.",
                "static/assembled_electrical/hexaboard_in_riser.jpg"
            ),
            DisplayStep(
                "Power Cables",
                "Connect power cables to the hexaboard. Be careful to orient the connector board appropriately, as although it can be installed backwards, attempting to power the board while so will destroy it.",
                "static/assembled_electrical/power_cables.jpg"
            ),
            DisplayStep(
                "Trophy-Hexaboard",
                "Connect the hexaboard to a trophy. Some force may need applied. Support the test stand with your hand from below. The boards will connect with an audible snap.",
                "static/assembled_electrical/hexaboard_trophy.jpg"
            ),
            DisplayStep(
                "Trophy-Kria",
                "If not alreact connected, attach the trophy to the Kria. The boards will connect silently.",
                "static/assembled_electrical/kria_trophy.jpg"
            ),
            DisplayStep(
                "L3 Loopback",
                "Connect the L3 Loopback to the hexaboard. The board should not overlap with the trophy. When correctly, the hole in the L3 Loopback chip will be centered on a support pillar below.",
                "static/assembled_electrical/l3_loopback.jpg"
            ),
            VerifyStep(
                "Setup Inspection",
                "Ensure the following flags have been met",
                [
                    "Power Cables Oriented Properly",
                    "Trophy Oriented Properly",
                    "L3 Loopback Installed Properly"
                ],
                "static/assembled_electrical/l3_loopback.jpg"
            )
        ]

        self._runtime_steps = [
            DynamicThreadStep("Power Supply", "The power supply should be enabled.", enable_power_supply), # TODO ["Channel 1 is powered", "Channel 2 is unpowered"]
            DynamicThreadStep("Kria", "Ensure the central LEDs on the Kria have turned blue.", partial(enable_kria, config.get_kria_web_address())),
            DynamicThreadStep("Load Config", "Loading the board's configuration files...", load_config, True, "board_config"),
            DynamicThreadStep("Load Redis", "Loading Redis Templates...", open_redis, True, "redis"),
            DynamicThreadStep("Load Firmware", "Loading appropriate firmware for the hexaboard", partial(load_firmware, config.get_kria_web_address()), True),
            DynamicThreadStep("Restart Services", "Waiting for services to restart...", partial(restart_services, config.get_kria_web_address(), 0.05), True),
            DynamicThreadStep("Create Sockets", "Creating Sockets. If this hangs, something's gone wrong.", partial(create_sockets, config.get_kria_ip()), True, "sockets"),
            DynamicThreadStep("Power (Normal)", "Checking Power", check_power_default, True),
            # TODO Bias Voltage?
            # TODO I2C Space Check, with fail!
            DynamicThreadStep("Configure HGCROC", "Configuring the HGCROC...", configure_hgcroc, True),
            DynamicThreadStep("I2C Checker (2)", "Running the I2C Checker...", partial(i2c_checker_2, config.get_output_dir()), True),
            DynamicThreadStep("Power (Configured)", "Checking Power", check_power_configured, True),
            DynamicThreadStep("Initialize Sockets", "Initializing Sockets", initialize_sockets, True),
            DynamicThreadStep("Pedestal Run (1)", "Pedestal Run", partial(do_pedestal_run, config.get_output_dir()), True),
            DynamicThreadStep("Scans", "Running Scans", partial(do_scans, config.get_output_dir()), True),
            DynamicThreadStep("Pedestal Run (2)", "Pedestal Run", partial(do_pedestal_run, config.get_output_dir()), True),
        ]

        self._shutdown_steps = [
            DynamicThreadStep("Kria", "Ensure the central LEDs on the Kria are no longer blue.", partial(disable_kria, config.get_kria_web_address())),
            DynamicThreadStep("Power Supply", "The power supply should be disabled.", disable_power_supply),  # TODO ["Channel 1 is unpowered", "Channel 2 is unpowered"]
            DisplayStep("L3 Loopback", "Remove the L3 Loopback from the hexaboard"),
            DisplayStep("Trophy-Kria", "Disconnect the trophy from the Kria"),
            DisplayStep("Trophy-Hexaboard", "Disconnect the hexaboard from the trophy"),
            DisplayStep("Power Cables", "Connect power cables to the hexaboard"),
            DisplayStep("Sticker", "Pretend to place a sticker on the hexaboard"),
            DisplayStep("Remove Hexaboard", "Remove the hexaboard from the test stand"),
            DynamicThreadStep("Cleanup", "Archiving + Uploading Data", partial(cleanup, config.get_output_dir()), True),
        ]

    def get_steps(self, stage: TestStage) -> list[TestStep]:
        if stage == TestStage.SETUP:
            return self._setup_steps
        elif stage == TestStage.RUNTIME:
            return self._runtime_steps
        elif stage == TestStage.SHUTDOWN:
            return self._shutdown_steps