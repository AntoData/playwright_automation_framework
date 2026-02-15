import json
from utils import path_utils

def open_test_data_file(file_path: str) -> dict:
    root_path: str = path_utils.get_project_root()
    full_path: str = root_path + "/"  + file_path
    with open(full_path, "r") as file:
        return json.load(file)