from steps.input_steps import DisplayStep, VerifyStep, SelectStep, TextAreaStep
from steps.thread_steps import DynamicThreadStep

from objects import TestFlow, TestStage, TestStep

from .custom_steps.powersupply import *
from .custom_steps.kria import *
from .custom_steps.scanner import *
from .custom_steps.tests import *
from .custom_steps.cleanup import cleanup
from .watcher import Watcher

from functools import partial

import os

import yaml

# Required for unpack
class AssembledHexaboardFlow(TestFlow):
    def __init__(self):
        with open("flows/assembled_electrical/flow.yaml") as fin:
            self._config = yaml.safe_load(fin)

        os.environ["PATH"] = os.environ["PATH"] + ":" + os.path.abspath(os.path.join(self._config["config"]["hexactrl_sw_dir"], "bin"))

        self._setup_steps = load_steps(self._config["initialization"], self._config["config"])
        self._runtime_steps = load_steps(self._config["runtime"], self._config["config"])
        self._shutdown_steps = load_steps(self._config["shutdown"], self._config["config"])


    def get_steps(self, stage: TestStage) -> list[TestStep]:
        if stage == TestStage.SETUP:
            return self._setup_steps
        elif stage == TestStage.RUNTIME:
            return self._runtime_steps
        elif stage == TestStage.SHUTDOWN:
            return self._shutdown_steps
    
    def get_watcher(self, fetch_data) -> QWidget:
        kria_management_url = f"http://{self._config['config']['kria_address']}:{self._config['config']['kria_management_port']}"
        return Watcher(kria_management_url, fetch_data)

def load_steps(steps: object, config: object) -> list[TestStep]:
    loaded_steps = []
    for step in steps:
        skip_optional = config["skip_optional"] if "skip_optional" in config else False
        optional = step["optional"] if "optional" in step else False
        if skip_optional and optional:
            continue

        loaded_steps.append(load_step(step, config))

    return loaded_steps

# Load a step from YAML
def load_step(step: object, config: object) -> TestStep:
    try:
        if step["type"] == "display":
            return DisplayStep(step["name"], step["text"], step["image"] if "image" in step else None)
        elif step["type"] == "textarea":
            return TextAreaStep(step["name"], step["text"], step["data_field"])
        elif step["type"] == "verify":
            return VerifyStep(step["name"], step["text"], step["verifications"],
                step["image"] if "image" in step else None,
                step["error_on_missing"] if "error_on_missing" in step else None)
        
        easy_dynamic_thread = lambda method: DynamicThreadStep(
            step["name"],
            step["text"] if "text" in step else "Text Not Provided",
            method,
            step["auto_advance"] if "auto_advance" in step else None,
            step["data_field"] if "data_field" in step else None,
            step["timeout"] if "timeout" in step else 0)
        
        kria_management_url = f"http://{config['kria_address']}:{config['kria_management_port']}"

        # Custom Steps
        if step["type"] == "select_user":
            return SelectStep(step["name"], step["text"], config["users"])
        
        # Kria
        elif step["type"] == "kria_wait":
            return easy_dynamic_thread(partial(wait_for_kria, kria_management_url, step["delay"]))
        elif step["type"] == "kria_enable":
            return easy_dynamic_thread(partial(enable_kria, kria_management_url))
        elif step["type"] == "kria_load_firmware":
            return easy_dynamic_thread(partial(load_firmware, kria_management_url))
        elif step["type"] == "kria_restart_services":
            return easy_dynamic_thread(partial(restart_services, kria_management_url, step["delay"]))
        elif step["type"] == "kria_disable":
            return easy_dynamic_thread(partial(disable_kria, kria_management_url))

        # Power Supply
        elif step["type"] == "power_supply_wait":
            return easy_dynamic_thread(partial(wait_for_power_supply, config["power_supply_address"], step["delay"]))
        elif step["type"] == "power_supply_enable":
            return easy_dynamic_thread(enable_power_supply)
        elif step["type"] == "power_supply_disable":
            return easy_dynamic_thread(disable_power_supply)
        elif step["type"] == "power_supply_check_power_default":
            return easy_dynamic_thread(check_power_default)
        elif step["type"] == "power_supply_check_power_configured":
            return easy_dynamic_thread(check_power_configured)
        
        # Scanning, Board ID
        elif step["type"] == "scan_board":
            return CentralBarcodeStep(step["name"], step["text"], step["data_field"])
        elif step["type"] == "verify_board":
            return VerifyBoardStep(step["name"], step["data_field"])
        elif step["type"] == "scan_hgcrocs":
            return ScanHGCROCs(step["name"])
        
        # Actual Tests
        elif step["type"] == "create_dut":
            return easy_dynamic_thread(create_dut)
        elif step["type"] == "tests_open_sockets":
            return easy_dynamic_thread(partial(create_sockets,
                config["kria_address"],
                config["kria_i2c_port"],
                config["kria_daq_port"],
                config["local_daq_port"]))
        elif step["type"] == "tests_configure_hgcrocs":
            return easy_dynamic_thread(configure_hgcroc)
        elif step["type"] == "tests_i2c_checker_configured":
            return easy_dynamic_thread(partial(i2c_checker_configured, config["output_dir"]))
        elif step["type"] == "tests_initialize_sockets":
            return easy_dynamic_thread(initialize_sockets)
        elif step["type"] == "tests_pedestal_run":
            return easy_dynamic_thread(partial(do_pedestal_run, config["output_dir"]))
        elif step["type"] == "tests_pedestal_scan":
            return easy_dynamic_thread(partial(do_pedestal_scan, config["output_dir"]))
        elif step["type"] == "tests_vrefinv":
            return easy_dynamic_thread(partial(do_vrefinv, config["output_dir"]))
        elif step["type"] == "tests_vrefnoinv":
            return easy_dynamic_thread(partial(do_vrefnoinv, config["output_dir"]))
        
        # Cleanup
        elif step["type"] == "cleanup":
            return easy_dynamic_thread(partial(cleanup, config["output_dir"]))

    except Exception as e:
        raise ValueError("Invalid step", step, e)

    raise ValueError("Invalid Step", step)