from steps.input_steps import DisplayStep, VerifyStep, SelectStep, TextAreaStep
from steps.thread_steps import DynamicThreadStep

from objects import TestFlow, TestStage, TestStep

from .custom_steps.powersupplies import multimodule_distribution_hub, siglent_spd3303xe
from .custom_steps.kria import *
from .custom_steps.scanner import *
from .custom_steps.tests import *
from .custom_steps.cleanup import cleanup
from .watcher import Watcher

from functools import partial

import glob
import os

import yaml

# Required for unpack
class AssembledHexaboardFlow(TestFlow):
    def __init__(self):
        with open("flows/assembled_electrical/flow.yaml") as fin:
            self._config = yaml.safe_load(fin)

        os.environ["PATH"] = os.environ["PATH"] + ":" + os.path.abspath(os.path.join(self._config["config"]["hexactrl_sw_dir"], "bin"))
        
        config = self._config["config"]
        self.power_supply = None
        if config["power_supply"] == "siglent_spd3303xe":
            self.power_supply = siglent_spd3303xe
        elif config["power_supply"] == "multimodule_distribution_hub":
            self.power_supply = multimodule_distribution_hub
        else:
            logger.critical(f"Unknown power supply {config['power_supply']}")


        self._setup_steps = load_steps(self._config["initialization"], config, self.power_supply)
        self._runtime_steps = load_steps(self._config["runtime"], config, self.power_supply)
        self._shutdown_steps = load_steps(self._config["shutdown"], config, self.power_supply)


    def get_steps(self, stage: TestStage) -> list[TestStep]:
        if stage == TestStage.SETUP:
            return self._setup_steps
        elif stage == TestStage.RUNTIME:
            return self._runtime_steps
        elif stage == TestStage.SHUTDOWN:
            return self._shutdown_steps
    
    def get_watcher(self, fetch_data) -> QWidget:
        return Watcher(fetch_data, self.power_supply)

def load_steps(steps: object, config: object, power_supply: object) -> list[TestStep]:
    loaded_steps = []
    for step in steps:
        skip_optional = config["skip_optional"] if "skip_optional" in config else False
        optional = step["optional"] if "optional" in step else False
        if skip_optional and optional:
            continue

        if "enabled" in step and not step["enabled"]:
            continue

        loaded_steps.append(load_step(step, config, power_supply))

    return loaded_steps

def fetch_images(out_dir, pattern, data):
    if "USE_LATEST" in pattern:
        parts = pattern.split("USE_LATEST/")
        dirs = glob.glob(os.path.join(out_dir, data["dut"], parts[0], '*'))
        timestamps = [ int(os.path.basename(it).split("_")[1]) for it in dirs]
        path = dirs[0] if timestamps[0] > timestamps[1] else dirs[1]
        return glob.glob(os.path.join(path, parts[1]))
    return glob.glob(os.path.join(out_dir, data["dut"], pattern))

# Load a step from YAML
def load_step(step: object, config: object, power_supply: object) -> TestStep:
    try:
        if step["type"] == "display":
            return DisplayStep(step["name"], step["text"], step["image"] if "image" in step else None)
        elif step["type"] == "textarea":
            return TextAreaStep(step["name"], step["text"], step["data_field"])
        elif step["type"] == "verify":
            return VerifyStep(step["name"], step["text"], step["verifications"],
                step["image"] if "image" in step else None,
                step["error_on_missing"] if "error_on_missing" in step else None)
                
        kria_address = config['kria_address']
        output_dir = config["output_dir"]

        easy_dynamic_thread_with_validator = lambda method, validator: DynamicThreadStep(
            step["name"],
            step["text"] if "text" in step else "Text Not Provided",
            method,
            step["auto_advance"] if "auto_advance" in step else None,
            step["data_field"] if "data_field" in step else None,
            step["timeout"] if "timeout" in step else 0,
            validator)
        
        easy_dynamic_thread_with_files = lambda method, validator: DynamicThreadStep(
            step["name"],
            step["text"] if "text" in step else "Text Not Provided",
            method,
            step["auto_advance"] if "auto_advance" in step else None,
            step["data_field"] if "data_field" in step else None,
            step["timeout"] if "timeout" in step else 0,
            validator,
            partial(fetch_images, output_dir, step["files"]))

        easy_dynamic_thread = lambda method: easy_dynamic_thread_with_validator(method, None)

        # Custom Steps
        if step["type"] == "select_user":
            return SelectStep(step["name"], step["text"], config["users"])
        
        # Kria
        elif step["type"] == "kria_wait":
            return easy_dynamic_thread(partial(wait_for_kria, kria_address, step["delay"]))
        elif step["type"] == "kria_enable":
            return easy_dynamic_thread(enable_kria)
        elif step["type"] == "kria_load_firmware":
            return easy_dynamic_thread_with_validator(load_firmware, load_firmware_validator)
        elif step["type"] == "kria_restart_services":
            return easy_dynamic_thread(partial(restart_services, step["delay"]))
        elif step["type"] == "kria_disable":
            return easy_dynamic_thread(disable_kria)

        # Power Supply
        elif step["type"] == "power_supply_wait":
            return easy_dynamic_thread(partial(power_supply.wait_for_power_supply, config["power_supply_address"], step["delay"]))
        elif step["type"] == "power_supply_enable":
            return easy_dynamic_thread(power_supply.enable_power_supply)
        elif step["type"] == "power_supply_disable":
            return easy_dynamic_thread(power_supply.disable_power_supply)
        elif step["type"] == "power_supply_check_power_default":
            return easy_dynamic_thread(partial(do_check_power, power_supply))
        elif step["type"] == "power_supply_check_power_configured":
            return easy_dynamic_thread(partial(do_check_power, power_supply))
        
        # Scanning, Board ID
        elif step["type"] == "scan_board":
            return CentralBarcodeStep(step["name"], step["text"], step["data_field"])
        elif step["type"] == "verify_board":
            return VerifyBoardStep(step["name"], step["data_field"])
        elif step["type"] == "scan_hgcrocs":
            return ScanHGCROCs(step["name"])
        
        # Actual Tests
        elif step["type"] == "tests_open_sockets":
            return easy_dynamic_thread(partial(do_create_sockets,
                config["kria_address"],
                config["kria_i2c_port"],
                config["kria_daq_port"],
                config["local_daq_port"]))
        elif step["type"] == "tests_configure_hgcrocs":
            return easy_dynamic_thread(do_configure_hgcroc)
        elif step["type"] == "tests_i2c_checker_default":
            return easy_dynamic_thread_with_validator(partial(do_i2c_checker_default, output_dir), check_i2c)
        elif step["type"] == "tests_i2c_checker_configured":
            return easy_dynamic_thread_with_validator(partial(do_i2c_checker_configured, output_dir), check_i2c)
        elif step["type"] == "tests_initialize_sockets":
            return easy_dynamic_thread(do_initialize_sockets)
        elif step["type"] == "tests_pedestal_run":
            return easy_dynamic_thread_with_files(partial(do_pedestal_run, output_dir), check_pedestal_run)
        elif step["type"] == "tests_pedestal_scan":
            return easy_dynamic_thread_with_files(partial(do_pedestal_scan, output_dir), None)
        elif step["type"] == "tests_vrefinv":
            return easy_dynamic_thread_with_files(partial(do_vrefinv, output_dir), None)
        elif step["type"] == "tests_vrefnoinv":
            return easy_dynamic_thread_with_files(partial(do_vrefnoinv, output_dir), None)
        
        # Cleanup
        elif step["type"] == "cleanup":
            archive = True if "archive" not in step else step["archive"]
            return easy_dynamic_thread(partial(cleanup, config["output_dir"], archive))

    except Exception as e:
        raise ValueError("Invalid step", step, e)

    raise ValueError("Invalid Step", step)