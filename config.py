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
    format = "%(asctime)s - %(name)-24s - %(levelname)-7s - %(message)s (%(filename)s:%(lineno)d)"

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
            "Institution": "The University of Alabama",
            "Users": "Nathan N; Not Nathan N",
            "LogLevel": "DEBUG"
        }
        
        # Test Info
        self.config["AssembledBoards"] = {
            "HexactrlScript": "/opt/hexactrl-script",
            "HexactrlSoftware": "/opt/hexactrl/ROCv3",
            "OutputDir": "./data",
            "TestConfigTemplate": "./test_config_template.yaml",
            "PowerSupplyAddress": "TCPIP::10.116.24.138",
            "KriaAddress": "10.116.24.233"
        }
        
        # Read Config, Save
        self.config.read(configFile)
        with open(configFile, 'w') as file:
            self.config.write(file)


        # Setup color logging, log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.getLevelName(self.config["General"].get("LogLevel")))
        ch.setFormatter(Formatter())
        logging.basicConfig(
            level=self.config["General"].get("LogLevel").upper(),
            handlers=[ch]
        )

    # Actual Info
    def get_institution(self) -> str:
        return self.config["General"].get("Institution")
    
    def get_users(self) -> list[str]:
        return [user.strip() for user in self.config["General"].get("Users").split(";")]

    # Assembled Config Info
    def get_hexactrl_script_dir(self) -> str:
        return path.abspath(self.config["AssembledBoards"].get("HexactrlScript"))
    
    def get_hexactrl_software_dir(self) -> str:
        return path.abspath(self.config["AssembledBoards"].get("HexactrlSoftware"))
    
    def get_output_dir(self) -> str:
        return path.abspath(self.config["AssembledBoards"].get("OutputDir"))
    
    def get_test_config_template_path(self) -> str:
        return path.abspath(self.config["AssembledBoards"].get("TestConfigTemplate"))
    
    def get_power_supply_address(self) -> str:
        return self.config["AssembledBoards"].get("PowerSupplyAddress")
    
    # Kria Settings
    def get_kria_ip(self) -> str:
        return self.config["AssembledBoards"].get("KriaAddress")
    
    def get_kria_web_address(self) -> str:
        print(self.get_kria_ip())
        return f"http://{self.get_kria_ip()}:8080"
    
config = Config("config.ini")