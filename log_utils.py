import logging

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
    

# Saves logs to a variable until said variable is wiped
logs = []
class VariableHandler(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)

    def emit(self, record):
        logs.append(format(record))

# Initialize logging config
def setup_logging():
    # Setup color logging,
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(Formatter())

    varHandler = VariableHandler()

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[ch, varHandler]
    )

    logging.info("Setup Logging")