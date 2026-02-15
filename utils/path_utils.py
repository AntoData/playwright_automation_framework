"""
Utility functions for handling file paths in the project.
"""
import os

def get_project_root() -> str:
    """
    Retrieves the root directory of the project.
    :return: A string representing the absolute path to the root
    directory of the project.
    :rtype: str
    """
    current_path: str = os.path.abspath(__file__)
    project_root: str = os.path.dirname(os.path.dirname(current_path))
    return project_root