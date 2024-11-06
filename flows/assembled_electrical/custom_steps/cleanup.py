import logging
import tarfile
import shutil
import os
import json

import log_utils

logger = logging.getLogger("Cleanup")

# Compression Util
def filter_no_logs(info: tarfile.TarInfo) -> tarfile.TarInfo:
    if info.name.endswith(".raw") or info.name.endswith(".log") or info.name.endswith(".png"):
        return None
    return info

# Compresses all test data to a tar.gz
# This excludes analysis (eg. plots) and only includes raw data
def archive_test(data_dir: str, test_id: str, delete_uncompressed: False) -> None:
    logger.info(f"Archiving { test_id }")
    archive_path = os.path.join(data_dir, f"{ test_id }.tar.gz")
    
    # Check if we've done this before
    if os.path.exists(archive_path):
        logger.warning(f"File { archive_path } already exists! Skipping...")
        return
    
    # Create archive
    with tarfile.open(archive_path, "w:gz") as tar:
        logger.debug(f"Writing final output")

        # Add Files
        if os.path.exists(os.path.join(data_dir, test_id)):
            for file in os.listdir(os.path.join(data_dir, test_id)):
                logger.debug(f"Writing { file }")
                tar.add(os.path.join(data_dir, test_id, file), file, filter=filter_no_logs)
    
    if delete_uncompressed:
        logger.info("Removing uncompressed data")
        shutil.rmtree(os.path.join(data_dir, test_id))

# Full Cleanup of all tests
def cleanup(out_dir: str, archive: bool, data: object) -> None:
    dut = data["dut"]
    logger.debug(f"Using dut {dut}")

    # Create dir if not exist
    if not os.path.exists(os.path.join(out_dir, dut)):
        os.mkdir(os.path.join(out_dir, dut))

    # Write output json
    filtered_data = {}
    for key in data:
        if key.startswith("_"):
            continue
        filtered_data[key] = data[key]

    data_text = json.dumps(filtered_data, indent=2)

    with open(os.path.join(out_dir, dut, "output.json"), "w") as file:
        file.write(data_text)

    logger.critical("This will the the final log for this test - further ones will be wiped")
    with open(os.path.join(out_dir, dut, "log.log"), "w") as file:
        file.write("\n".join(log_utils.logs))

    # Archive Data
    if archive:
        logger.info("Archiving tests")
        archive_test(out_dir, dut, True)
