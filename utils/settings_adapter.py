"""
This module defines the SettingsAdapter abstract base class, which
serves as a blueprint for creating adapters that connect to various
configuration sources and retrieve settings as dictionaries. Subclasses
 of SettingsAdapter must implement the connect method to specify how to
access the configuration source and fetch the settings. This design
allows for flexible and customizable connections to different types of
configuration sources, such as files, databases, or external services,
ensuring that settings are retrieved correctly and securely.
"""
import abc
from pathlib import Path

class SettingsAdapter(abc.ABC):
    """
    Abstract base class that defines the interface for connecting to a
    configuration source and retrieving settings as a dictionary.
    Subclasses must implement the connect method to specify how to
    access the configuration source and fetch the settings.
    """
    @classmethod
    @abc.abstractmethod
    def connect(cls, resource_path: str | Path):
        """
        Abstract method to connect to a configuration source and
        retrieve settings as a dictionary. Subclasses must implement
        this method to specify how to connect to the configuration
        and fetch the settings.

        :param resource_path: A string or Path representing the path to the
        configuration resource (e.g., file path, database connection
        string, API endpoint, etc.) if needed by the adapter to fetch
        the settings. It should be a folder over the root of the
        project.
        :type resource_path: str | Path
        :return: A dictionary containing the configuration settings
        retrieved from the specified resource.
        :rtype: dict
        """
        pass
