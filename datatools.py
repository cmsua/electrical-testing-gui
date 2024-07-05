# This file is for use by whoever processes data for the database
# If you're testing hexaboards, this file is not for you!

import json
import os
import xml.etree.ElementTree as ET

data_dir = "./data"

def add_subelements(element: ET.Element, subelements: dict[str: str]) -> ET.Element:
    for key in subelements:
        add_subelement(element, key, subelements[key])
    return element

def add_subelement(element: ET.Element, name: str, value: str) -> ET.Element:
    subelement = ET.SubElement(element, name)
    subelement.text = value
    return subelement

def file_to_elements(data_set, board: str) -> None:
    path = f"{data_dir}/{board}.json"
    with open(path, 'r') as file:
        data = json.loads(file.read())[board]

        part = ET.SubElement(data_set, "PART", { "mode": "auto"})
        add_subelements(part, {
            "SERIAL_NUMBER": "TODO",
            "BARCODE": board,
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

if __name__ == "__main__":
    data_set = ET.Element("DATA_SET")
    comment_description = ET.SubElement(data_set, "COMMENT_DESCRIPTION")
    comment_description.text = "Upload functional tests data"

    version = ET.SubElement(data_set, "VERSION")
    version.text = str(1)

    for file in os.listdir(data_dir):
        if not file.endswith(".json"):
            continue

        file_to_elements(data_set, file.replace(data_dir, "").replace(".json", ""))

    tree = ET.ElementTree(data_set)
    ET.indent(tree, space="\t", level=0)
    tree.write(f"{ data_dir }/output.xml")