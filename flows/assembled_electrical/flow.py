from steps.input_steps import DisplayStep, VerifyStep, SelectStep, TextAreaStep
from steps.thread_steps import DynamicThreadStep

from objects import TestFlow, TestStage, TestStep

from flows.assembled_electrical.powersupply import *
from flows.assembled_electrical.kria import *
from flows.assembled_electrical.redis import *
from flows.assembled_electrical.scanner import *
from flows.assembled_electrical.tests import *
from flows.assembled_electrical.cleanup import cleanup

from functools import partial

import os

import yaml

# Required for unpack
class AssembledHexaboardFlow(TestFlow):
    def __init__(self):
        with open("flows/assembled_electrical/flow.yaml") as fin:
            self._config = yaml.safe_load(fin)

        os.environ["PATH"] = os.environ["PATH"] + ":" + os.path.abspath(os.path.join(self._config["config"]["hexactrl_sw_dir"], "bin"))

        self._setup_steps = [load_step(step, self._config["config"]) for step in self._config["initialization"]]
        self._runtime_steps = [load_step(step, self._config["config"]) for step in self._config["runtime"]]
        self._shutdown_steps = [load_step(step, self._config["config"]) for step in self._config["shutdown"]]


    def get_steps(self, stage: TestStage) -> list[TestStep]:
        if stage == TestStage.SETUP:
            return self._setup_steps
        elif stage == TestStage.RUNTIME:
            return self._runtime_steps
        elif stage == TestStage.SHUTDOWN:
            return self._shutdown_steps
    
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
            return ScanHGCROCs(step["name"], step["data_field"])
        
        # Actual Tests
        elif step["type"] == "load_config":
            return easy_dynamic_thread(load_config)
        elif step["type"] == "connect_redis_load_template":
            return easy_dynamic_thread(open_redis)
        elif step["type"] == "tests_open_sockets":
            return easy_dynamic_thread(partial(create_sockets, config["kria_address"]))
        elif step["type"] == "tests_configure_hgcrocs":
            return easy_dynamic_thread(configure_hgcroc)
        elif step["type"] == "tests_i2c_checker":
            return easy_dynamic_thread(partial(i2c_checker_2, config["output_dir"]))
        elif step["type"] == "tests_pedestal_run":
            return easy_dynamic_thread(partial(do_pedestal_run, config["output_dir"]))
        elif step["type"] == "tests_initialize_sockets":
            return easy_dynamic_thread(initialize_sockets)
        elif step["type"] == "tests_trimming":
            return easy_dynamic_thread(partial(do_trimming, config["output_dir"]))
        
        # Cleanup
        elif step["type"] == "cleanup":
            return easy_dynamic_thread(partial(cleanup, config["output_dir"]))

    except Exception as e:
        raise ValueError("Invalid step", step, e)

    raise ValueError("Invalid Step", step)