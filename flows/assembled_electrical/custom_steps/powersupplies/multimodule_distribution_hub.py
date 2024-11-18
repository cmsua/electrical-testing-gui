import time
import paramiko
import logging
import json
import threading
import traceback

logger = logging.getLogger("powersupply")

module = "1"

# Try and connect to the supply every X s.
def wait_for_power_supply(address: str, delay: int, data: object):
    while True:
        logger.debug(f"Attempting to connect to the power supply at {address}")
        try:
            client = paramiko.client.SSHClient()
            client.load_system_host_keys()
            client.connect(address, username="powercontrol")
            logger.info("Connected to power supply")
            
            # Disable Power
            client.exec_command(f"cd ~/Desktop; ./venv/bin/python mm_tester_tray_simple.py --module {module} --off")

            return {'client': client, 'lock': threading.Lock()}
        except Exception as e:
            logger.warning(f"Exception when connecting to kria: {e}\n{traceback.format_exc()}")

        time.sleep(delay)

def enable_power_supply(data):
    data["_power_supply"]["lock"].acquire()
    data["_power_supply"]["client"].exec_command(f"cd ~/Desktop; ./venv/bin/python mm_tester_tray_simple.py --module {module} --on")
    data["_power_supply"]["lock"].release()

def check_power(data):
    data["_power_supply"]["lock"].acquire()
    stdin, stdout, stderr = data["_power_supply"]["client"].exec_command(f"cd ~/Desktop; ./venv/bin/python mm_tester_tray_simple.py --module {module} --status")

    stdout = stdout.read().decode()
    stderr = stderr.read().decode()
    data["_power_supply"]["lock"].release()

    logger.debug(f"Response gotten: stdout: {stdout}\n\nstderr: {stderr}")
    returned_data = json.loads(stdout)

    result = {
        "voltage": returned_data[f"IN_VOLTAGE"],
        "state": returned_data[f"MODULE_{module}_STATE"],
        "state_analog": returned_data[f"MODULE_{module}_ANALOG_STATE"],
        "state_digital": returned_data[f"MODULE_{module}_DIGITAL_STATE"],
        "current": returned_data[f"MODULE_{module}_ANALOG_CURRENT"] + returned_data["MODULE_1_DIGITAL_CURRENT"],
        "current_digital": returned_data[f"MODULE_{module}_DIGITAL_CURRENT"],
        "current_analog": returned_data[f"MODULE_{module}_ANALOG_CURRENT"]
    }

    logger.debug(f"Read from Power Supply: {result}")
    return result

def disable_power_supply(data):
    logger.info("Disabling Channel 1")
    data["_power_supply"]["lock"].acquire()
    data["_power_supply"]["client"].exec_command(f"cd ~/Desktop; ./venv/bin/python mm_tester_tray_simple.py --module {module} --off")
    data["_power_supply"]["client"].close()
    data["_power_supply"]["lock"].release()