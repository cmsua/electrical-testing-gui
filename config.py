import configparser
import logging
from os import path

# Code from https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
# This formatter is for pretty logs
class Formatter(logging.Formatter):
    grey = "\x1b[37m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[1;31m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)-20s - %(levelname)-7s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: logging.Formatter(grey + format + reset),
        logging.INFO: logging.Formatter(format),
        logging.WARNING: logging.Formatter(yellow + format + reset),
        logging.ERROR: logging.Formatter(red + format + reset),
        logging.CRITICAL: logging.Formatter(bold_red + format + reset)
    }

    def format(self, record):
        return self.FORMATS.get(record.levelno).format(record)
    
# Config Class
class Config:
    def __init__(self, configFile: str) -> None:
        self.config = configparser.ConfigParser()

        # Defaults
        self.config["General"] = {
            "HexactrlScript": "",
            "HexactrlSoftware": "",
            "OutputDir": "./data",
            "TestConfigs": "./configs",
            "TestConfigTemplate": "./test_config_template.yaml",
            "Database": "postgresql://username:password@hostname/database",
            "LogLevel": "Info",
            "DaqClientPortStart": 7000
        }

        self.config["Hexacontroller.Default"] = {
            "Name": "Unnamed",
            "ZynqPort": 8080,
            "DaqServerPort": 6000,
            "I2CServerPort": 5555,
            "SSHPort": 22
        }

        # Read Config, Save
        self.config.read(configFile)
        with open(configFile, 'w') as file:
            self.config.write(file)

        # Add Daq Client Ports
        controllers = self.getHexacontrollers()
        daq_client_port_start = int(self.config["General"].get("daqclientportstart"))
        for i in range(len(controllers)):
            self.config.set(controllers[i], "DaqClientPort", str(daq_client_port_start + i))

        # Setup color logging, log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.getLevelName(self.config["General"].get("LogLevel")))
        ch.setFormatter(Formatter())
        logging.basicConfig(
            level=self.config["General"].get("LogLevel").upper(),
            handlers=[ch]
        )

    def getHexactrlScriptDir(self) -> str:
        return path.abspath(self.config["General"].get("HexactrlScript"))
    
    def getHexactrlSoftwareDir(self) -> str:
        return path.abspath(self.config["General"].get("HexactrlSoftware"))
    
    def getOutputDir(self) -> str:
        return path.abspath(self.config["General"].get("OutputDir"))

    def getDatabaseString(self) -> str:
        return self.config["General"].get("Database")
    
    def getTestConfigTemplate(self) -> str:
        return path.abspath(self.config["General"].get("TestConfigTemplate"))
    
    def getTestConfigDir(self) -> str:
        return path.abspath(self.config["General"].get("TestConfigs"))
    
    # List all established hexacontrollers
    def getHexacontrollers(self) -> str:
        sections = self.config.sections()
        sections.remove("General")
        sections.remove("Hexacontroller.Default")
        return sections
    
    # Internal method
    def __getHexacontrollerValue(self, controllerId: str, value: str) -> str:
        return self.config[controllerId].get(value, self.config["Hexacontroller.Default"].get(value))

    def getHexacontrollerName(self, controllerId: str) -> str:
        return self.__getHexacontrollerValue(controllerId, "Name")
    
    # No fallback supported here
    def getHexacontrollerAddress(self, controllerId: str) -> str:
        return self.config[controllerId].get("Address")
    
    def getHexacontrollerZynqPort(self, controllerId: str) -> str:
        return self.__getHexacontrollerValue(controllerId, "ZynqPort")
    
    def getHexacontrollerDaqServerPort(self, controllerId: str) -> str:
        return self.__getHexacontrollerValue(controllerId, "DaqServerPort")
    
    def getHexacontrollerDaqClientPort(self, controllerId: str) -> str:
        return self.__getHexacontrollerValue(controllerId, "DaqClientPort")
    
    def getHexacontrollerI2CServerPort(self, controllerId: str) -> str:
        return self.__getHexacontrollerValue(controllerId, "I2CServerPort")
    
    def getHexacontrollerSSHPort(self, controllerId: str) -> str:
        return self.__getHexacontrollerValue(controllerId, "SSHPort")
    
config = Config("config.ini")