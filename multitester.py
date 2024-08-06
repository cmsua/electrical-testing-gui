from PyQt6.QtCore import QThread, pyqtSignal

from config import config

import os, logging, subprocess, io, re, requests

from ansi2html import Ansi2HTMLConverter
console_color = re.compile(r"\[\d{,3}(;\d{,3}){4}m")
converter = Ansi2HTMLConverter()

def setup_test(id, board, hgroc0, hgroc1, hgroc2, timestamp) -> None:
    logger = logging.getLogger(id)
    logger.info("Setting up test for " + id)
    
    # Create Config
    testConfigPath = os.path.join(config.getTestConfigDir(), id + ".yaml")
    outDir = f"{ config.getOutputDir() }"
    with open(config.getTestConfigTemplate(), "r") as template:
        testConfig = template.read()
        
        # Replace key values
        testConfig = testConfig.replace("TOKEN_BOARD_BARCODE", board + "-" + timestamp)
        testConfig = testConfig.replace("TOKEN_ROC_0_BARCODE", hgroc0)
        testConfig = testConfig.replace("TOKEN_ROC_1_BARCODE", hgroc1)
        testConfig = testConfig.replace("TOKEN_ROC_2_BARCODE", hgroc2)
        testConfig = testConfig.replace("TOKEN_HEXACONTROLLER_ADDRESS", config.getHexacontrollerAddress(id))
        testConfig = testConfig.replace("TOKEN_ZYNQ_PORT", config.getHexacontrollerZynqPort(id))
        testConfig = testConfig.replace("TOKEN_DAQ_CLIENT_PORT", config.getHexacontrollerDaqClientPort(id))
        testConfig = testConfig.replace("TOKEN_DAQ_SERVER_PORT", config.getHexacontrollerDaqServerPort(id))
        testConfig = testConfig.replace("TOKEN_I2C_SERVER_PORT", config.getHexacontrollerI2CServerPort(id))
        testConfig = testConfig.replace("TOKEN_OUTDIR", outDir)

        # Create Config Dir if not exists
        if not os.path.exists(config.getTestConfigDir()):
            logger.info(f"Test config directory does not exist. Creating {config.getTestConfigDir()}")
            os.makedirs(config.getTestConfigDir())

        # Write Config
        with open(testConfigPath, "w") as testConfigFile:
            testConfigFile.write(testConfig)
            logger.debug(f"Written test config to {testConfigFile}")

    # Create Output Dir if not exists
    if not os.path.exists(outDir):
        logger.info(f"Output directory does not exist. Creating {outDir}")
        os.makedirs(outDir)

    return testConfigPath

# Thread to run tests
# Ran in the background to not cause messes
class TestThread(QThread):
    # Line Out Signal
    line = pyqtSignal(str)
    exit = pyqtSignal(int)

    def __init__(self, id, name, timestamp):
        super().__init__()
        self.id = id
        self.name = name
        self.timestamp = timestamp
    
    def run(self) -> None:
        logger = logging.getLogger(self.id)
        logger.info("Starting test for " + self.id)

        # Recreate environment and such
        env = os.environ.copy()
        env["PATH"] = f"{ config.getHexactrlSoftwareDir() }/bin:{ env['PATH'] }"
        env["PYTHONPATH"] = f"{ config.getHexactrlScriptDir() }/analysis:{ config.getHexactrlScriptDir() }"
        env["SOURCE"] = f"{ config.getHexactrlScriptDir() }/analysis/etc/env.sh"
        env["BASEDIR"] = f"{ config.getHexactrlScriptDir() }/analysis"

        # Power On Board
        logger.debug("Powering On Hexaboard")
        command_url = f"http://{ config.getHexacontrollerAddress(self.id) }:{ config.getHexacontrollerZynqPort(self.id) }/command"
        power_status = requests.put(command_url, json={ "name": "pwr_on" })
        logger.debug(f"Hexaboard is powered with status { power_status.json() }")

        # Start Processes
        logger.debug("Starting DAQ Client")
        daqClientLog = open(f"{ config.getOutputDir() }/{ self.name }-{ self.timestamp }-daq-client.log", "w")
        daqClient = subprocess.Popen([ f"{ config.getHexactrlSoftwareDir() }/bin/daq-client", "-p", str(config.getHexacontrollerDaqClientPort(self.id)) ], stdout=daqClientLog, stderr=subprocess.STDOUT)
        
        logger.debug("Starting Test Process")
        testConfigPath = os.path.join(config.getTestConfigDir(), self.id + ".yaml")
        testLog = open(f"{ config.getOutputDir() }/{ self.name }-{ self.timestamp }.log", "w")
        proc = subprocess.Popen([ "./venv/bin/python3", "hexaboard-V3B-production-test-ua.py", "-i", testConfigPath ], env=env, cwd=config.getHexactrlScriptDir(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Read process till done
        for line in io.TextIOWrapper(proc.stdout, encoding='utf-8'):
            line = console_color.sub("", line)

            testLog.write(line)
            self.line.emit(converter.convert(line))

        # Exit, get return code
        returncode = proc.poll()
        if returncode == None:
            logger.error("Test script not finished, killing! This should be an impossible state!")
            proc.kill()
            returncode = 1

        # Log exit, kill daq client
        logger.info(f"Tests finished with exit code {returncode}, Killing Daq Client")
        daqClient.kill()

        daqClientLog.close()
        testLog.close()

        # Power Off Board
        logger.debug("Powering Off Hexaboard")
        power_status = requests.put(command_url, json={ "name": "pwr_off" })
        logger.debug(f"Hexaboard is unpowered with status { power_status }")

        # Emit Exit Code
        self.exit.emit(returncode)