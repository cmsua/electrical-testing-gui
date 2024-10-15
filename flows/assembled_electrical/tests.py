import yaml
import logging
import os
import sys
import io
import contextlib
import uuid

from .powersupply import check_power
from hexactrl_script import zmq_controler as zmqctrl
from hexactrl_script import i2c_checker
from hexactrl_script import pedestal_run
from hexactrl_script import pedestal_scan
from hexactrl_script import vrefinv_scan
from hexactrl_script import vrefnoinv_scan

logger = logging.getLogger("tests")


# Load Config Files
def load_config(data: object) -> object:
    logger.info("Loading Config...")

    if data["board"] == "ld-full":
        file = "flows/assembled_electrical/XLFL_production_test_ua.yaml" # TODO Read From Data
    else:
        raise ValueError(f"Board {data['board']} not implemented!")
    logger.debug(f"Identified config as {file}")

    with open(file) as fin:
        logger.debug("Opened File")

        test_config = yaml.safe_load(fin)
        logger.debug(f"Read File as {test_config}")

        # Load Parsed Data
        test_config['rocs'] = data['hgcrocs']
        test_config['dut'] = str(uuid.uuid4())
        return test_config


# Not sure what this does
def create_sockets(address: str, data: object) -> object:
    config_file = os.path.join("hexactrl_script", data["board_config"]["daq_and_fe_configuration"])
    logger.debug(f"Identified config as {config_file}")

    i2c_port = data["board_config"]["i2cPort"]
    daq_port = data["board_config"]["daqPort"]
    puller_port = data["board_config"]["pullerPort"]
    logger.debug(f"Identified I2C Port {i2c_port}, DAQ Server Port {daq_port}, Puller Port {puller_port}")
    logger.debug(f"Using address {address} for the Kria")

    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            sockets =  {
                "i2c": zmqctrl.i2cController(address, i2c_port, config_file, "DEBUG"),
                "daq": zmqctrl.daqController(address, daq_port, config_file, "DEBUG"),
                "cli": zmqctrl.daqController('localhost' , puller_port, config_file, "DEBUG")
            }
    logger.debug(f"Loading sockets wrote to stdout/stderr: {output.getvalue()}")

    return sockets


# Check power supply data, calcualte power,
# and save to redis
def check_power_default(data: object) -> None:
    logger.info("Checking default power for the board")

    result = check_power(data)
    power = result["current"] * result["voltage"]
    logger.debug(f"Recieved {result} (Power: {power}), saving to Redis")

    data["redis"].set("POWER:DEFAULT", power)


# Not sure what this does
def configure_hgcroc(data: object) -> None:
    logger.info("Configuring HGCROC")
    data["sockets"]["i2c"].initialize()


# Check the i2c again
def i2c_checker_2(output_dir: str, data: object) -> None:
    logger.info("2nd I2C check after configuring")
    # The original script loaded the config again
    # That's a bit silly - we don't need to do that
    # Just used the cached version

    dut = data["board_config"]["dut"]
    logger.info(f"Using dut {dut}")

    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            i2c_checker.i2c_checker(data["sockets"]["i2c"], output_dir, dut, data["board_config"])
    logger.debug(f"i2c_checker wrote to stdout/stderr: {output.getvalue()}")

    redis = data["redis"]
    if redis.get('TEST_SUCCESS')=='FAIL':
        logger.critical(f'I2C Failed!')
        redis.set('I2C_CHECKER:CONFIGURED','FAIL')
        raise RuntimeError("I2C Failed!")
    else:
        redis.set('I2C_CHECKER:CONFIGURED','SUCCESS')

# Check power supply data, calcualte power,
# and save to redis
def check_power_configured(data: object) -> None:
    logger.info("Checking configured power for the board")

    result = check_power(data)
    power = result["current"] * result["voltage"]
    logger.debug(f"Recieved {result} (Power: {power}), saving to Redis")

    data["redis"].set("POWER:CONFIGURED", power)

# Not sure what this does either
def initialize_sockets(data: object) -> None:
    logger.info("Initializing sockets")
    
    # I2C, wrap stdout/stderr
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            data["sockets"]["i2c"].initialize()
    logger.debug(f"Initialized I2C Socket; Wrote to stdout/stderr: {output.getvalue()}")

    # DAQ Server, wrap stdout/stderr
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            data["sockets"]["daq"].initialize()
    logger.debug(f"Initialized DAQ Socket; Wrote to stdout/stderr: {output.getvalue()}")

    server_ip = data["sockets"]["daq"].ip
    logger.info(f"Using {server_ip} as daq sever ip for client puller")
    data["sockets"]["cli"].yamlConfig['client']['serverIP'] = server_ip

    # Puller, wrap stdout/stderr
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            data["sockets"]["cli"].initialize()
    logger.debug(f"Initialized Puller Socket; Wrote to stdout/stderr: {output.getvalue()}")

# Pedestal Run
# Can't name it pedestal_run due to a name conflict
def do_pedestal_run(output_dir: str, data: object) -> None:
    logger.info("Doing a pedestal run!")

    dut = data["board_config"]["dut"]
    logger.debug(f"Using dut {dut}")
    
    # Do pedestal run, wrap stdout/stderr
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            pedestal_run.pedestal_run(data["sockets"]["i2c"], data["sockets"]["daq"], data["sockets"]["cli"], output_dir, dut, "", "DEBUG")
    logger.info(f"Pedestal Run Complete, wrote to stdout/stderr: {output.getvalue()}")

    redis = data["redis"]
    if redis.get('PEDESTAL_RUN:CORRUPTION')=='FAIL':
        logger.critical("Data corruption was found in pedestal data.")
        raise RuntimeError("I2C Failed!")
    else:
        logger.info("Pedestal Run Passed")

# Run All Other Scans
def do_trimming(output_dir: str, data: object) -> None:
    logger.info("Doing all scans!")

    dut = data["board_config"]["dut"]
    logger.debug(f"Using dut {dut}")
    
    i2c_socket = data["sockets"]["i2c"]
    daq_socket = data["sockets"]["daq"]
    cli_socket = data["sockets"]["cli"]

    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            pedestal_scan.pedestal_scan(i2c_socket, daq_socket, cli_socket, output_dir, dut)
    logger.debug(f"Pedestal Scan Complete, produced output {output.getvalue()}")

    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            vrefinv_scan.vrefinv_scan(i2c_socket, daq_socket, cli_socket, output_dir, dut)
    logger.debug(f"VRefInv Scan Complete, produced output {output.getvalue()}")

    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            vrefnoinv_scan.vrefnoinv_scan(i2c_socket, daq_socket, cli_socket, output_dir, dut)
    logger.debug(f"VRefNoInv Scan Complete, produced output {output.getvalue()}")

def close_sockets(data: object) -> None:
    logger.info("Closing sockets")
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            data["sockets"]["i2c"].close()
            data["sockets"]["daq"].close()
            data["sockets"]["cli"].close()
    logger.debug(f"Closing Sockets Complete, produced output {output.getvalue()}")