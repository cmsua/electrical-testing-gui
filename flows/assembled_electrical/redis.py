import logging
import os

from hexactrl_script import redis_interface as redis_interface
from steps.thread_steps import DynamicThreadStep

logger = logging.getLogger("redis")

class DynamicThreadStepWithRedisCheck(DynamicThreadStep):
    def __init__(self, name: str, message: str, method, auto_advance: bool=False, data_field: str=None, timeout: int=0) -> None:
        super().__init__(name, message, method, auto_advance, data_field, timeout)

    def get_output_status(self, in_data, out_data) -> list[str]:
        test_status = in_data["redis"].get('TEST_SUCCESS')
        logger.debug(f"Got {test_status} at the end of step during verification")

        if test_status == 'FAIL':
            return ['yellow']
        elif test_status == 'SUCCESS':
            return ['green']
        return ['blue']

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