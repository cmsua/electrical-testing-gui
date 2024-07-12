# This file is for use by whoever processes data for the database
# If you're testing hexaboards, this file is not for you!

import json
import os
import shutil
import tarfile
import logging
import xml.etree.ElementTree as ET

from config import config
logger = logging.getLogger("datatools")

# XML Utilities
def add_subelements(element: ET.Element, subelements: dict[str: str]) -> ET.Element:
    for key in subelements:
        add_subelement(element, key, subelements[key])
    return element

def add_subelement(element: ET.Element, name: str, value: str) -> ET.Element:
    subelement = ET.SubElement(element, name)
    subelement.text = value
    return subelement

# Convert a test to xml components for dbuploader
# Uses format provided by CERN
def file_to_elements(data_set: ET.SubElement, test_id: str, board_id: str) -> None:
    logger.info(f"Creating XML tags for { test_id }")
    path = f"{ data_dir }/{ test_id }.json"
    with open(path, 'r') as file:
        data = json.loads(file.read())[test_id]

        part = ET.SubElement(data_set, "PART", { "mode": "auto"})
        add_subelements(part, {
            "SERIAL_NUMBER": "TODO",
            "BARCODE": board_id,
            "KIND_OF_PART": "Hexaboard HD Full"
        })

        data_tag = ET.SubElement(data_set, "DATA")
        add_subelements(data_tag, {
            "TESTED_BY": "TODO",
            "TEST_DATE": str(os.path.getmtime(path)),
            "HGCROC_POS_0": data["ROC0"],
            "HGCROC_POS_1": data["ROC1"],
            "HGCROC_POS_2": data["ROC2"],
            "HGCROC_POS_3": "N/A",
            "HGCROC_POS_4": "N/A",
            "HGCROC_POS_5": "N/A",
            "POWER_DEFAULT": data["POWER:DEFAULT"],
            "POWER_DEFAULT_RESULT": "N/A",
            "POWER_CONFIGURED": data["POWER:CONFIGURED"],
            "POWER_CONFIGURED_RESULT": "N/A",
            "I2C_CHECKER_DEFAULT": data["I2C_CHECKER:DEFAULT"],
            "I2C_CHECKER_CONFIGURED": data["I2C_CHECKER:CONFIGURED"],
            "BV_VMON": "TODO",
            "BV_IMON": "TODO",
            "BV_RESULT": "TODO",
            "PEDESTAL_RUN_0_0_NOISE": data["PEDESTAL_RUN:0:0:NOISE"],
            "PEDESTAL_RUN_0_0_NUMBER_CHANNELS_NOISE_AT0": data["PEDESTAL_RUN:0:0:NUMBER_CHANNELS_NOISE_AT0"],
            "PEDESTAL_RUN_0_0_NUMBER_CHANNELS_NOISE_MORE2": data["PEDESTAL_RUN:0:0:NUMBER_CHANNELS_NOISE_MORE2"],
            "PEDESTAL_RUN_0_1_NOISE": data["PEDESTAL_RUN:0:1:NOISE"],
            "PEDESTAL_RUN_0_1_NUMBER_CHANNELS_NOISE_AT0": data["PEDESTAL_RUN:0:1:NUMBER_CHANNELS_NOISE_AT0"],
            "PEDESTAL_RUN_0_1_NUMBER_CHANNELS_NOISE_MORE2": data["PEDESTAL_RUN:0:1:NUMBER_CHANNELS_NOISE_MORE2"],
            "PEDESTAL_RUN_1_0_NOISE": data["PEDESTAL_RUN:1:0:NOISE"],
            "PEDESTAL_RUN_1_0_NUMBER_CHANNELS_NOISE_AT0": data["PEDESTAL_RUN:1:0:NUMBER_CHANNELS_NOISE_AT0"],
            "PEDESTAL_RUN_1_0_NUMBER_CHANNELS_NOISE_MORE2": data["PEDESTAL_RUN:1:0:NUMBER_CHANNELS_NOISE_MORE2"],
            "PEDESTAL_RUN_1_1_NOISE": data["PEDESTAL_RUN:1:1:NOISE"],
            "PEDESTAL_RUN_1_1_NUMBER_CHANNELS_NOISE_AT0": data["PEDESTAL_RUN:1:1:NUMBER_CHANNELS_NOISE_AT0"],
            "PEDESTAL_RUN_1_1_NUMBER_CHANNELS_NOISE_MORE2": data["PEDESTAL_RUN:1:1:NUMBER_CHANNELS_NOISE_MORE2"],
            "PEDESTAL_RUN_2_0_NOISE": data["PEDESTAL_RUN:2:0:NOISE"],
            "PEDESTAL_RUN_2_0_NUMBER_CHANNELS_NOISE_AT0": data["PEDESTAL_RUN:2:0:NUMBER_CHANNELS_NOISE_AT0"],
            "PEDESTAL_RUN_2_0_NUMBER_CHANNELS_NOISE_MORE2": data["PEDESTAL_RUN:2:0:NUMBER_CHANNELS_NOISE_MORE2"],
            "PEDESTAL_RUN_2_1_NOISE": data["PEDESTAL_RUN:2:1:NOISE"],
            "PEDESTAL_RUN_2_1_NUMBER_CHANNELS_NOISE_AT0": data["PEDESTAL_RUN:2:1:NUMBER_CHANNELS_NOISE_AT0"],
            "PEDESTAL_RUN_2_1_NUMBER_CHANNELS_NOISE_MORE2": data["PEDESTAL_RUN:2:1:NUMBER_CHANNELS_NOISE_MORE2"],
            "PEDESTAL_RUN_3_0_NOISE": "N/A",
            "PEDESTAL_RUN_3_0_NUMBER_CHANNELS_NOISE_AT0": "N/A",
            "PEDESTAL_RUN_3_0_NUMBER_CHANNELS_NOISE_MORE2": "N/A",
            "PEDESTAL_RUN_3_1_NOISE": "N/A",
            "PEDESTAL_RUN_3_1_NUMBER_CHANNELS_NOISE_AT0": "N/A",
            "PEDESTAL_RUN_3_1_NUMBER_CHANNELS_NOISE_MORE2": "N/A",
            "PEDESTAL_RUN_4_0_NOISE": "N/A",
            "PEDESTAL_RUN_4_0_NUMBER_CHANNELS_NOISE_AT0": "N/A",
            "PEDESTAL_RUN_4_0_NUMBER_CHANNELS_NOISE_MORE2": "N/A",
            "PEDESTAL_RUN_4_1_NOISE": "N/A",
            "PEDESTAL_RUN_4_1_NUMBER_CHANNELS_NOISE_AT0": "N/A",
            "PEDESTAL_RUN_4_1_NUMBER_CHANNELS_NOISE_MORE2": "N/A",
            "PEDESTAL_RUN_5_0_NOISE": "N/A",
            "PEDESTAL_RUN_5_0_NUMBER_CHANNELS_NOISE_AT0": "N/A",
            "PEDESTAL_RUN_5_0_NUMBER_CHANNELS_NOISE_MORE2": "N/A",
            "PEDESTAL_RUN_5_1_NOISE": "N/A",
            "PEDESTAL_RUN_5_1_NUMBER_CHANNELS_NOISE_AT0": "N/A",
            "PEDESTAL_RUN_5_1_NUMBER_CHANNELS_NOISE_MORE2": "N/A",
            "CHANNEL_IDS_NOISE_AT0": "N/A",
            "CHANNEL_IDS_NOISE_MORE2": "N/A",
            "PEDESTAL_RUN_NOISE_AT0_RESULT": "N/A",
            "PEDESTAL_RUN_NOISE_MORE2_RESULT": "N/A",
            "TEST_RESULT": data["TEST_SUCCESS"],
            "GENERAL_COMMENTS": "N/A",
            "FULL_DATA": "TODO"
        })

        return (part, data_tag)

# Compression Util
def filter_no_logs(info: tarfile.TarInfo) -> tarfile.TarInfo:
    if info.name.endswith(".raw") or info.name.endswith(".log") or info.name.endswith(".png"):
        return None
    return info

# Compresses all test data to a tar.gz
# This excludes analysis (eg. plots) and only includes raw data
def archive_test(test_id: str, delete_uncompressed: False) -> None:
    logger.info(f"Archiving { test_id }")
    data_dir = config.getOutputDir()
    archive_path = f"{ data_dir }/{ test_id }.tar.gz"
    
    # Check if we've done this before
    if os.path.exists(archive_path):
        logger.warn(f"File { archive_path } already exists! Skipping...")
        return
    
    # Create archive
    with tarfile.open(archive_path, "w:gz") as tar:
        logger.debug(f"Writing final output")
        tar.add(f"{ data_dir }/{ test_id }.json", "output.json")

        logger.debug(f"Writing logs")
        tar.add(f"{ data_dir }/{ test_id }.log", "output.log")
        tar.add(f"{ data_dir }/{ test_id }-daq-client.log", "daq-client.log")

        for file in os.listdir(f"{ data_dir }/{ test_id }"):
            logger.debug(f"Writing { file }")
            tar.add(f"{ data_dir }/{ test_id }/{ file }", file, filter=filter_no_logs)
    
    if delete_uncompressed:
        logger.info("Removing uncompressed data")
        shutil.rmtree(f"{ data_dir }/{ test_id }")
        os.remove(f"{ data_dir }/{ test_id }.json")
        os.remove(f"{ data_dir }/{ test_id }.log")
        os.remove(f"{ data_dir }/{ test_id }-daq-client.log")

if __name__ == "__main__":
    # Create root elements
    data_set = ET.Element("DATA_SET")
    comment_description = ET.SubElement(data_set, "COMMENT_DESCRIPTION")
    comment_description.text = "Upload functional tests data"

    version = ET.SubElement(data_set, "VERSION")
    version.text = str(1)

    # Start processing data
    data_dir = config.getOutputDir()
    logger.info(f"Loading tests from { data_dir }")

    for file in os.listdir(data_dir):
        if not file.endswith(".json"):
            continue
        
        # Get info
        test_id = file.replace(data_dir, "").replace(".json", "")
        board_id = test_id.split("-")[0]

        logger.info(f"Processing board { board_id } under test { test_id }")

        # Save to xml
        file_to_elements(data_set, test_id, board_id)
        archive_test(test_id, True)

    # Write output xml
    logger.info(f"Writing output data to { data_dir }/output.xml")
    tree = ET.ElementTree(data_set)
    ET.indent(tree, space="\t", level=0)
    tree.write(f"{ data_dir }/output.xml")
    
    logger.info("Exiting.")