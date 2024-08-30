import logging
import tarfile
import shutil
import os
import json
import io

logger = logging.getLogger("Cleanup")

# Compression Util
def filter_no_logs(info: tarfile.TarInfo) -> tarfile.TarInfo:
    if info.name.endswith(".raw") or info.name.endswith(".log") or info.name.endswith(".png"):
        return None
    return info

# Compresses all test data to a tar.gz
# This excludes analysis (eg. plots) and only includes raw data
def archive_test(data_dir: str, test_id: str, delete_uncompressed: False, redis_data: object) -> None:
    logger.info(f"Archiving { test_id }")
    archive_path = f"{ data_dir }/{ test_id }.tar.gz"
    
    # Check if we've done this before
    if os.path.exists(archive_path):
        logger.warn(f"File { archive_path } already exists! Skipping...")
        return
    
    # Create archive
    with tarfile.open(archive_path, "w:gz") as tar:
        logger.debug(f"Writing final output")

        # Add Redis Data
        redis_data_text = json.dumps(redis_data, indent=2)
        logger.debug(f"Adding redis data {redis_data_text}")

        redis_bytes = redis_data_text.encode('utf-8')
        redis_bytes_io = io.BytesIO(redis_bytes)
        
        file_info = tarfile.TarInfo('run.log')
        file_info.size = len(redis_bytes)
        tar.addfile(file_info, redis_bytes_io)

        # Add Files
        for file in os.listdir(f"{ data_dir }/{ test_id }"):
            logger.debug(f"Writing { file }")
            tar.add(f"{ data_dir }/{ test_id }/{ file }", file, filter=filter_no_logs)
    
    if delete_uncompressed:
        logger.info("Removing uncompressed data")
        shutil.rmtree(f"{ data_dir }/{ test_id }")

# Full Cleanup of all tests
def cleanup(out_dir: str, data: object) -> None:
    if "board_config" not in data:
        logger.critical("Didn't get far enough to load configs, so no data to archive!")
        return
    
    dut = data["board_config"]["config"]["dut"]
    logger.debug(f"Using dut {dut}")

    logger.info("Dumping Redis")
    redis_data = data["redis"].client.hgetall(dut)

    logger.info("Archiving tests")
    archive_test(out_dir, dut, True, redis_data)
