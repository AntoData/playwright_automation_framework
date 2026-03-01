"""
Utility functions for handling file paths in the project.
"""
from pathlib import Path

def get_project_root() -> Path:
    """
    Retrieves the root directory of the project.
    :return: A Path representing the absolute path to the root
    directory of the project.
    :rtype: Path
    """
    return Path(__file__).resolve().parent.parent
