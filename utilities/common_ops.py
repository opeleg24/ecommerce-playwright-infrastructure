import json
import time
import xml.etree.ElementTree as ET


def get_time_stamp():
    return time.time()

####################################################################################################################
# Function Name:get_data
# Function Description: This function is used to get data from data.xml file
# Function Parameters: node_name
# Function Return: String - node value
####################################################################################################################
def get_data(node_name):
    # jenkins
    #root = ET.parse("../configuration/data.xml").getroot()
    # pytest
    root = ET.parse("./configuration/data.xml").getroot()
    return root.find('.//' + node_name).text

####################################################################################################################
# Function Name: read_json_file
# Function Description: This function is used to read json file
# Function Parameters: file_path
# Function Return: json file
####################################################################################################################
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

####################################################################################################################
# Function Name: calculate_total_price
# Function Description: This function is used to calculate the total price
# Function Parameters: quantity, price
# Function Return: int - total price
####################################################################################################################
def calculate_total_price(quantity: int, price: int):
    total = quantity * price
    return total

####################################################################################################################
# Function Name: split_string
# Function Description: This function is used to split a string and return the first part as int
# Function Parameters: text
# Function Return: int - first part of the split string
####################################################################################################################
def split_string(text: str):
    text_split = text.split(" ")
    return int(text_split[0])
