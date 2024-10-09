import configparser
import logging
from os import path
    
# Config Class
class Config:
    logger = logging.getLogger("config")
    def __init__(self, config_file: str) -> None:
        self.config = configparser.ConfigParser()
        config_file_path = path.abspath(config_file)

        # Defaults
        self.config["General"] = {
            "Institution": "The University of Alabama",
            "Users": "Nathan N; Not Nathan N"
        }
        
        # Test Info
        self.config["AssembledBoards"] = {
            "HexactrlSoftware": "/opt/hexactrl/ROCv3",
            "OutputDir": "./data",
            "PowerSupplyAddress": "TCPIP::10.116.24.138",
            "KriaAddress": "10.116.24.233"
        }
        
        # Read Config, Save
        self.logger.info(f"Reading config from {config_file_path}")
        self.config.read(config_file_path)
        with open(config_file_path, 'w') as file:
            self.logger.info(f"Saving config to {config_file_path}")
            self.config.write(file)

        # Log Values
        self.logger.debug(f"Read values {self.config.values}")

    # Actual Info
    def get_institution(self) -> str:
        return self.config["General"].get("Institution")
    
    def get_users(self) -> list[str]:
        return [user.strip() for user in self.config["General"].get("Users").split(";")]

    # Assembled Config Info
    # This is only used for Unpack and nothing else
    def get_hexactrl_software_dir(self) -> str:
        return path.abspath(self.config["AssembledBoards"].get("HexactrlSoftware"))
    
    def get_output_dir(self) -> str:
        return path.abspath(self.config["AssembledBoards"].get("OutputDir"))
    
    def get_power_supply_address(self) -> str:
        return self.config["AssembledBoards"].get("PowerSupplyAddress")
    
    # Kria Settings
    def get_kria_ip(self) -> str:
        return self.config["AssembledBoards"].get("KriaAddress")
    
    def get_kria_web_address(self) -> str:
        return f"http://{self.get_kria_ip()}:8080"
    
config = Config("config.ini")