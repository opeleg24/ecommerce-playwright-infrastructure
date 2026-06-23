import json
import time
import xml.etree.ElementTree as ET

CONFIG_FILE_PATH = "./configuration/data.xml"


def get_time_stamp() -> float:
    """Return the current Unix timestamp in seconds."""
    return time.time()


def get_data(node_name: str) -> str:
    """Return the text value of a node from the configuration XML file.

    Raises ValueError when the requested node is not present.
    """
    root = ET.parse(CONFIG_FILE_PATH).getroot()
    node = root.find(f'.//{node_name}')
    if node is None:
        raise ValueError(f"Config node not found: node_name={node_name}")
    return node.text


def read_json_file(file_path: str) -> dict:
    """Read and parse a JSON file, returning its decoded contents."""
    with open(file_path, 'r') as json_file:
        return json.load(json_file)


def calculate_total_price(quantity: int, price: int) -> int:
    """Return the total price for the given quantity at the given unit price."""
    return quantity * price


def split_string(text: str) -> int:
    """Split on whitespace and return the first segment parsed as an int."""
    text_split = text.split(" ")
    return int(text_split[0])
