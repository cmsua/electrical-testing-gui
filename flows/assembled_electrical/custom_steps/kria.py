import time
import logging
import traceback

import paramiko

from objects import TestFinishedBehavior

logger = logging.getLogger("kria")

pins = [52, 53, 57]

# Try and connect to the Kria every X s.
def wait_for_kria(address: str, delay: int, data: object) -> None:
    while True:
        logger.debug(f"Attempting to connect to the kria at {address}")
        try:
            client = paramiko.client.SSHClient()
            client.load_system_host_keys()
            client.connect(address, username="root") # TODO This is insecure - why!
            logger.info("Connected to Kria")
            
            # Enable Pin States
            for pin in pins:
                client.exec_command(f"echo {str(pin)} > /sys/class/gpio/export")
                client.exec_command(f"echo \"out\" > /sys/class/gpio/gpio{str(pin)}/direction")

            return client
        except Exception as e:
            logger.warning(f"Exception when connecting to kria: {e}\n{traceback.format_exc()}")

        time.sleep(delay)

# Power on the Kria
def enable_kria(data: object) -> None:
    logger.debug(f"Attempting to power on the the kria")

    client = data["_kria"]
    for pin in pins:
        client.exec_command(f"echo 1 > /sys/class/gpio/gpio{str(pin)}/value")

# Power off the Kria
def disable_kria(data: object) -> None:
    logger.debug(f"Attempting to power off the the kria")

    client = data["_kria"]
    for pin in pins:
        client.exec_command(f"echo 0 > /sys/class/gpio/gpio{str(pin)}/value")
    client.close()

# Load firmware onto the board
def load_firmware(data: object) -> None:
    logger.debug(f"Attempting to load firmware for the kria")
    client = data["_kria"]

    # TODO
    stdin, stdout, stderr = client.exec_command("fw-loader load hexaboard-hd-tester-v2p0-trophy-v3")

    stdout = stdout.read().decode()
    stderr = stderr.read().decode()

    logger.debug(f"Response gotten: stdout: {stdout}\n\nstderr: {stderr}")
    time.sleep(5)
    return (stdout, stderr)

def load_firmware_validator(in_data: None, out_data: None) -> None:
    if out_data[1] != "":
        return {
            "color": "Red",
            "message": "See Console",
            "behavior": TestFinishedBehavior.SKIP_TO_CLEANUP
        }
    else:
        return True

# Restart Services
def restart_services(delay: int, data: object) -> None:
    logger.debug(f"Attempting to restart on the kria")
    client = data["_kria"]

    restart_response = client.exec_command("service daq-server restart")[1].read().decode()
    logger.debug(f"Restarted daq with response {restart_response}")
    time.sleep(3)
    
    restart_response = client.exec_command("service i2c-server restart")[1].read().decode()
    logger.debug(f"Restarted i2c with response {restart_response}")

    # Wait for daq alive
    while True:
        logger.debug(f"Querying DAQ Server status on the kria")
        stdin, stdout, stderr = client.exec_command("service daq-server status")
        response = stdout.read().decode()

        logger.debug(f"Resposne gotten: {response}")

        if "active (running)" not in response:
            logger.debug("DAQ not online")
        else:
            logger.debug("DAQ online")
            break

        time.sleep(delay)

    # Wait for i2c alive
    while True:
        logger.debug(f"Querying I2C Server status on the kria")
        stdin, stdout, stderr = client.exec_command("service i2c-server status")
        response = stdout.read().decode()

        logger.debug(f"Resposne gotten: {response}")

        if "active (running)" not in response:
            logger.debug("I2C not online")
        else:
            logger.debug("I2C online")
            break

        time.sleep(delay)