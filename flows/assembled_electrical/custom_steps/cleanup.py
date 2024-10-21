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
def archive_test(data_dir: str, test_id: str, delete_uncompressed: False, data: object) -> None:
    logger.info(f"Archiving { test_id }")
    archive_path = os.path.join(data_dir, f"{ test_id }.tar.gz")
    
    # Check if we've done this before
    if os.path.exists(archive_path):
        logger.warning(f"File { archive_path } already exists! Skipping...")
        return
    
    # Create archive
    with tarfile.open(archive_path, "w:gz") as tar:
        logger.debug(f"Writing final output")

        # Add Data
        data_text = json.dumps(data, indent=2)
        logger.debug(f"Adding data {data_text}")

        data_bytes = data_text.encode('utf-8')
        data_bytes_io = io.BytesIO(data_bytes)
        
        file_info = tarfile.TarInfo('run.log')
        file_info.size = len(data_bytes)
        tar.addfile(file_info, data_bytes_io)

        # Add Files
        if os.path.exists(os.path.join(data_dir, test_id)):
            for file in os.listdir(os.path.join(data_dir, test_id)):
                logger.debug(f"Writing { file }")
                tar.add(os.path.join(data_dir, test_id, file), file, filter=filter_no_logs)
    
    if delete_uncompressed:
        logger.info("Removing uncompressed data")
        shutil.rmtree(os.path.join(data_dir, test_id))

# Full Cleanup of all tests
def cleanup(out_dir: str, data: object) -> None:
    dut = data["dut"]
    logger.debug(f"Using dut {dut}")

    logger.info("Archiving tests")
    filtered_data = {}
    for key in data:
        if key.startswith("_"):
            continue
        filtered_data[key] = data[key]
    archive_test(out_dir, dut, True, filtered_data)
