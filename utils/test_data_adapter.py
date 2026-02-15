"""
Helper to manage test data stored as json
"""
import json
from utils import path_utils

def open_test_data_file(file_path: str) -> dict:
    """
    Open test data file in JSON format
    :param file_path: Relative path to test data file
    :type file_path: str
    :return: Dictionary of test data file
    :rtype: dict
    """
    root_path: str = path_utils.get_project_root()
    full_path: str = root_path + "/"  + file_path
    with open(full_path, "r") as file:
        return json.load(file)