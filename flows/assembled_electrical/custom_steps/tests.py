import yaml
import logging
import os
import sys
import io
import contextlib
import uuid

from objects import TestFinishedBehavior
from .. import boards
from hexactrl_script import zmq_controler as zmqctrl
from hexactrl_script import i2c_checker
from hexactrl_script import pedestal_run
from hexactrl_script import pedestal_scan
from hexactrl_script import vrefinv_scan
from hexactrl_script import vrefnoinv_scan

logger = logging.getLogger("tests")

# Not sure what this does
def do_create_sockets(address: str, kria_i2c_port: int, kria_daq_port: int, puller_port: int, data: object) -> object:
    config_file = boards.boards[data["_board"]]["board_config"]

    config_file = os.path.join("hexactrl_script", config_file)
    logger.debug(f"Identified config as {config_file}")

    logger.debug(f"Identified I2C Port {kria_i2c_port}, DAQ Server Port {kria_daq_port}, Puller Port {puller_port}")
    logger.debug(f"Using address {address} for the Kria")

    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            sockets =  {
                "i2c": zmqctrl.i2cController(address, kria_i2c_port, config_file, "DEBUG"),
                "daq": zmqctrl.daqController(address, kria_daq_port, config_file, "DEBUG"),
                "cli": zmqctrl.daqController('localhost' , puller_port, config_file, "DEBUG")
            }
    logger.debug(f"Loading sockets wrote to stdout/stderr: {output.getvalue()}")

    return sockets

# Check power supply data, calcualte power,
def do_check_power(power_supply: object, data: object) -> None:
    logger.info("Checking power for the board")

    result = power_supply.check_power(data)
    power = result["current"] * result["voltage"]
    logger.debug(f"Recieved {result} (Power: {power})")

    # TODO What are acceptable values here?
    return power

# Not sure what this does
def do_configure_hgcroc(data: object) -> None:
    logger.info("Configuring HGCROC")
    data["_sockets"]["i2c"].initialize()
    # TODO No Output


# Check the i2c again
def do_i2c_checker_default(output_dir: str, data: object) -> None:
    logger.info("I2C check after power on")

    dut = data["dut"]
    logger.debug(f"Using dut {dut}")

    # Load Config
    config_file = boards.boards[data["_board"]]["i2c_default_values"]
    config_file = os.path.join("hexactrl_script", config_file)
    logger.debug(f"Using I2C Default config file {config_file}")

    with open(config_file) as fin:
        default1ROC = yaml.safe_load(fin)
        config = {}
        for key in data["_sockets"]["i2c"].yamlConfig.keys():
            if key.find('roc_s')==0:
                config[key]={"sc":default1ROC}
                    
    # Run Checker
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            result = i2c_checker.i2c_checker(data["_sockets"]["i2c"], output_dir, dut, config, logging.getLogger("I2C Checker"))
    logger.debug(f"i2c_checker wrote to stdout/stderr: {output.getvalue()}")

    return result

# Check the i2c again
def do_i2c_checker_configured(output_dir: str, data: object) -> None:
    logger.info("2nd I2C check after configuring")
    # The original script loaded the config again
    # That's a bit silly - we don't need to do that
    # Just used the cached version

    dut = data["dut"]
    logger.info(f"Using dut {dut}")

    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            result = i2c_checker.i2c_checker(data["_sockets"]["i2c"], output_dir, dut, "", logging.getLogger("I2C Checker"))
    logger.debug(f"i2c_checker wrote to stdout/stderr: {output.getvalue()}")

    return result

def check_i2c(in_data, out_data):
    if out_data == i2c_checker.I2CCheckerSuccess.SUCCESS:
        return True
    elif out_data == i2c_checker.I2CCheckerSuccess.FAILURE:
        return {
            "message": "Failed!",
            "color": "red",
            "behavior": TestFinishedBehavior.NEXT_STEP
        }
    else:
        return {
            "message": f"Invalid Status {out_data}",
            "color": "red",
            "behavior": TestFinishedBehavior.NEXT_STEP
        }

# Not sure what this does either
def do_initialize_sockets(data: object) -> None:
    logger.info("Initializing sockets")
    
    # I2C, wrap stdout/stderr
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            data["_sockets"]["i2c"].initialize()
    logger.debug(f"Initialized I2C Socket; Wrote to stdout/stderr: {output.getvalue()}")

    # DAQ Server, wrap stdout/stderr
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            data["_sockets"]["daq"].initialize()
    logger.debug(f"Initialized DAQ Socket; Wrote to stdout/stderr: {output.getvalue()}")

    server_ip = data["_sockets"]["daq"].ip
    logger.info(f"Using {server_ip} as daq sever ip for client puller")
    data["_sockets"]["cli"].yamlConfig['client']['serverIP'] = server_ip

    # Puller, wrap stdout/stderr
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            data["_sockets"]["cli"].initialize()
    logger.debug(f"Initialized Puller Socket; Wrote to stdout/stderr: {output.getvalue()}")

# Pedestal Run
# Can't name it pedestal_run due to a name conflict
def do_pedestal_run(output_dir: str, data: object) -> None:
    logger.info("Doing a pedestal run!")

    dut = data["dut"]
    logger.debug(f"Using dut {dut}")
    
    # Do pedestal run, wrap stdout/stderr
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            returned_data = pedestal_run.pedestal_run(data["_sockets"]["i2c"], data["_sockets"]["daq"], data["_sockets"]["cli"], output_dir, dut, "", "DEBUG")
    logger.info(f"Pedestal Run complete, returned {data}")
    logger.debug(f"Pedestal Run wrote to stdout/stderr: {output.getvalue()}")

    out_data = { "_explode": True }
    for key in returned_data:
        out_data[f"PEDESTAL_RUN:{key}"] = returned_data[key]
    return out_data
    
def check_pedestal_run(input_data: object, data: object) -> object:
    if data["PEDESTAL_RUN:CORRUPTION"] == "FAIL":
        return {
            "color": "red",
            "message": "Data corruption in pedestal data",
            "behavior": TestFinishedBehavior.SKIP_TO_CLEANUP
        }
    elif "PEDESTAL_RUN:TEST_SUCCESS" in data and data["PEDESTAL_RUN:TEST_SUCCESS"] == "FAIL":
        return {
            "color": "red",
            "message": "Failed",
            "behavior": TestFinishedBehavior.NEXT_STEP
        }
    elif "PEDESTAL_RUN:TEST_SUCCESS" in data and data["PEDESTAL_RUN:TEST_SUCCESS"] != "FAIL":
        return {
            "color": "red",
            "message": f"Unknown Status {data['PEDESTAL_RUN:TEST_SUCCESS']}",
            "behavior": TestFinishedBehavior.NEXT_STEP
        }
    else:
        return True
    
# Do a Pedestal Scan
def do_pedestal_scan(output_dir: str, data: object) -> None:
    logger.info("Doing a pedestal scan!")
    dut = data["dut"]
    logger.debug(f"Using dut {dut}")
    
    i2c_socket = data["_sockets"]["i2c"]
    daq_socket = data["_sockets"]["daq"]
    cli_socket = data["_sockets"]["cli"]

    out_data = { "_explode": True }
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            returned_data = pedestal_scan.pedestal_scan(i2c_socket, daq_socket, cli_socket, output_dir, dut)

    for key in returned_data:
        out_data[f"TRIM_INV:{key}"] = returned_data[key]
        
    logger.info(f"Pedestal Scan Complete, returned {returned_data}")
    logger.debug(f"Pedestal Scan Complete, wrote to stdout/stderr {output.getvalue()}")

    return out_data

# Do a vrefinv
def do_vrefinv(output_dir: str, data: object) -> None:
    logger.info("Doing a vrefinv")
    dut = data["dut"]
    logger.debug(f"Using dut {dut}")
    
    i2c_socket = data["_sockets"]["i2c"]
    daq_socket = data["_sockets"]["daq"]
    cli_socket = data["_sockets"]["cli"]

    out_data = { "_explode": True }
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            returned_data = vrefinv_scan.vrefinv_scan(i2c_socket, daq_socket, cli_socket, output_dir, dut)

    for key in returned_data:
        out_data[f"INV_VREF:{key}"] = returned_data[key]
        
    logger.info(f"VRefInv Scan Complete, produced output {returned_data}")
    logger.debug(f"VRefInv Scan Complete, wrote to stdout/stderr {output.getvalue()}")

    return out_data

# Do a vrefnoinv
def do_vrefnoinv(output_dir: str, data: object) -> None:
    logger.info("Doing a vrefnoinv")
    dut = data["dut"]
    logger.debug(f"Using dut {dut}")
    
    i2c_socket = data["_sockets"]["i2c"]
    daq_socket = data["_sockets"]["daq"]
    cli_socket = data["_sockets"]["cli"]

    out_data = { "_explode": True }
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            returned_data = vrefnoinv_scan.vrefnoinv_scan(i2c_socket, daq_socket, cli_socket, output_dir, dut)
            for key in returned_data:
                out_data[f"NOINV_VREF:{key}"] = returned_data[key]

    for key in returned_data:
        out_data[f"NOINV_VREF:{key}"] = returned_data[key]
        
    logger.debug(f"VRefNoInv Scan Complete, produced output {returned_data}")
    logger.debug(f"VRefNoInv Scan Complete, wrote to stdout/stderr {output.getvalue()}")

    return out_data

def do_close_sockets(data: object) -> None:
    logger.info("Closing sockets")
    with contextlib.redirect_stdout(io.StringIO()) as output:
        with contextlib.redirect_stderr(sys.stdout):
            data["_sockets"]["i2c"].close()
            data["_sockets"]["daq"].close()
            data["_sockets"]["cli"].close()
    logger.debug(f"Closing Sockets Complete, produced output {output.getvalue()}")