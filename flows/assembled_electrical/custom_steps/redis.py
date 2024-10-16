import logging
import os

from hexactrl_script.analysis.level0 import redis_interface as redis_interface
from steps.thread_steps import DynamicThreadStep

logger = logging.getLogger("redis")

class DynamicThreadStepWithRedisCheck(DynamicThreadStep):
    def __init__(self, name: str, message: str, method, auto_advance: bool=False, data_field: str=None, timeout: int=0) -> None:
        super().__init__(name, message, method, auto_advance, data_field, timeout)

    def get_output_action(self, in_data, out_data) -> list[str]:
        test_status = in_data["redis"].get('TEST_SUCCESS')
        logger.debug(f"Got {test_status} at the end of step during verification")

        if test_status == 'FAIL':
            return False
        elif test_status == 'PASS':
            return True
        return { "color": "blue", "message": f"Invalid state {test_status}", "status": "fail" }

# Open Redis, Init Template
def open_redis(template: str, data: object) -> None:
    key = data["dut"]

    logger.info(f"Opening Redis with key {key}")
    redis_intf = redis_interface.RedisInterface(key)
    
    logger.debug(f"Loading tempalte {template}")
    redis_intf.initFromTemplate(template)

    logger.debug(f"Loading ROCs {data['hgcrocs']}")

    roc_dict = {}
    for index in range(len(data["hgcrocs"])):
        roc_dict[f'ROC{index}'] = data["hgcrocs"][index]
    redis_intf.set_multiple(roc_dict)

    return redis_intf