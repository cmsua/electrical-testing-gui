import logging
import os

from hexactrl_script import redis_interface as redis_interface

logger = logging.getLogger("redis")

# Open Redis, Init Template
def open_redis(data):
    key = data["board_config"]["config"]["dut"]

    logger.info(f"Opening Redis with key {key}")
    redis_intf = redis_interface.RedisInterface(key)
    
    template = os.path.join("hexactrl_script", data["board_config"]["config"]["redis_template"])
    logger.debug(f"Loading tempalte {template}")
    redis_intf.initFromTemplate(template)

    rocs = data["board_config"]["rocs"]
    logger.debug("Loading ROCs {rocs}")
    redis_intf.set_multiple(rocs)

    return redis_intf