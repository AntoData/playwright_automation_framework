"""
This module defines the ConfigFileAdapter class, which serves as an
adapter for connecting to ini configuration files and retrieving
settings as a dictionary.
"""
import configparser
from pathlib import Path
from utils import path_utils
from utils import settings_adapter

class ConfigFileAdapter(settings_adapter.SettingsAdapter):
    """
    Adapter class for connecting to ini configuration files and
    retrieving settings as a dictionary.
    """
    @classmethod
    def connect(cls, resource_path: str | Path) -> dict:
        """
        Connects to a configuration file and retrieves settings as a
        dictionary.

        :param resource_path: A string or Path representing the path to the
        configuration file (e.g., "config/config.ini"). It should be a
        folder over the root of the project.
        :type resource_path: str | Path
        :return: A dictionary containing the configuration settings
        retrieved from the specified file.
        :rtype: dict
        """

        normalized_resource_path = Path(resource_path)
        full_path: Path = path_utils.get_project_root() / normalized_resource_path
        config = configparser.ConfigParser()
        config.read(full_path)
        settings_dict: dict = {}
        for section in config.sections():
            for key, value in config[section].items():
                settings_dict[key] = value
        return settings_dict
