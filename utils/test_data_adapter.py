"""
Helper to manage test data stored as json
"""
import json
from pathlib import Path
from utils import path_utils

def open_test_data_file(file_path: str | Path) -> dict:
    """
    Open test data file in JSON format
    :param file_path: Relative path to test data file
    :type file_path: str | Path
    :return: Dictionary of test data file
    :rtype: dict
    """
    full_path: Path = path_utils.get_project_root() / Path(file_path)
    with full_path.open("r", encoding="utf-8") as file:
        return json.load(file)
