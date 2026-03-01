"""
This module provides a decorator function `settings_manager` that can be
used to manage settings for a class. The decorator takes a connector
(a type of `ConfigFileAdapter`), a path to the settings file,
and an optional list of settings to include. It retrieves the settings
 from the specified source and assigns them to the decorated class as a
class attribute named `settings`. This allows for easy access to
configuration settings within the class without needing to manually
load them each time.
"""
from pathlib import Path
from typing import Type, Callable
from utils import config_adapter


def settings_manager(connector: Type[config_adapter.ConfigFileAdapter],
                     path: str | Path,
                     settings_list: list[str] = None) -> Callable:
    """
    Class decorator that injects a `settings` dictionary into the
    decorated class.
    :param connector: A class that implements the ConfigFileAdapter
    interface, responsible for fetching the configuration settings.
    :type connector: Type[config_adapter.ConfigFileAdapter]
    :param path: Path to the configuration resource (e.g., file path,
     database connection string, API endpoint, etc.) if needed by the
     connector to fetch the settings.
    :type path: str | Path
    :param settings_list: An optional list of setting names to fetch.
    If None or empty, all settings from the specified source will be
    retrieved.
    :type settings_list: list[str] | None
    :return: Decorated class with an added `settings` attribute
    containing the retrieved settings.
    """
    def settings_manager_decorator(cls):
        settings_source: dict = connector.connect(path)
        settings_params: dict = {}
        for setting in settings_list:
            if settings_list is not None and len(settings_list) > 0:
                if setting in settings_list:
                    settings_params[setting] = settings_source[setting]
            else:
                settings_params = settings_source
        cls.settings = settings_params
        return cls
    return settings_manager_decorator
