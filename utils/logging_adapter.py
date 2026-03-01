"""
Provides a logging adapter that manages logging configuration and
handlers for consistent logging across the project. It includes a
settings class to manage logging settings from a configuration file, and
a logging adapter class that sets up file and console logging with
configurable log levels. The adapter also provides a hook for logging
uncaught exceptions.
"""
import sys
import logging
import types
from pathlib import Path
from typing import Optional, Type
from utils import settings_manager
from utils import config_adapter

@settings_manager.settings_manager(
    connector = config_adapter.ConfigFileAdapter,
    path = Path("config") / "config.ini",
    settings_list = ["log_level"])
class LogSettings:
    """
    Manages the settings for logging, such as log level and log file
    """
    settings: dict | None = None
    log_levels: dict = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET
    }


class LoggingAdapter:
    """
    Manages the creation of logs to log execution through
    different modules.
    """

    _log: Optional[logging.Logger] = None
    """
    :cvar _log: Instance of the logger this class will use
    :type _log: logging.Logger
    """

    _file_handler: Optional[logging.Handler] = None
    """
    :cvar _file_handler: Handler for logging to a file
    :type _file_handler: logging.Handler
    """

    _stream_handler: Optional[logging.Handler] = None
    """
    :cvar _stream_handler: Handler for logging to the console (stderr)
    :type _stream_handler: logging.Handler
    """

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Get the logger instance, creating it if it doesn't exist.
        :return: logger instance
        :rtype: logging.Logger
        """
        if cls._log is None:
            # If the logger doesn't exist, create it with a
            # stable name and configuration
            cls._log = logging.getLogger("TestLogger")
            cls._log.setLevel(LogSettings.log_levels[
                                  LogSettings.settings["log_level"]])
            cls._log.propagate = False  # prevents duplicates
        return cls._log

    @classmethod
    def setup(cls, file_name: str | Path, also_console: bool = True) -> (
            logging.Logger):
        """
        Configure per-tests logging to a file (and optionally stderr).
        Safe to call repeatedly: it replaces only *our* handlers.

        :param file_name: Path to the log file
        :type file_name: str
        :param also_console: Whether to also log to the console (stderr)
        :type also_console: bool
        :return: Configured logger instance
        :rtype: logging.Logger
        """
        logger = cls.get_logger()

        # Remove/close only handlers that were added by this class,
        # to avoid interfering with other logging configurations
        cls.teardown()

        # Ensure the directory for the log file exists
        log_file_path = Path(file_name)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a formatter that includes the logger name, level,
        # timestamp, line number, and message
        line_formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        # Create and add a file handler for logging to the specified
        # file
        cls._file_handler = logging.FileHandler(log_file_path, mode="w",
                                                encoding="utf-8")
        cls._file_handler.setLevel(
            LogSettings.log_levels[LogSettings.settings["log_level"]])
        cls._file_handler.setFormatter(line_formatter)
        logger.addHandler(cls._file_handler)

        # Optionally create and add a stream handler for logging
        # to the console (stderr)
        if also_console:
            cls._stream_handler = logging.StreamHandler(sys.stderr)
            cls._stream_handler.setLevel(
                LogSettings.log_levels[LogSettings.settings["log_level"]])
            cls._stream_handler.setFormatter(line_formatter)
            logger.addHandler(cls._stream_handler)

        return logger

    @classmethod
    def teardown(cls) -> None:
        """
        Close and remove our handlers.

        :return: None
        """
        # Remove/close only handlers that were added by this class,
        # to avoid interfering with other logging configurations
        logger: logging.Logger = cls._log
        if logger is None:
            return

        # For each handler we added, remove it from the logger and
        # close it to release resources
        for h in (cls._file_handler, cls._stream_handler):
            if h is not None:
                try:
                    logger.removeHandler(h)
                finally:
                    h.close()

        # Reset our handler references to None to indicate they are no
        # longer active
        cls._file_handler = None
        cls._stream_handler = None

    @staticmethod
    def exception_log_hook(exc_type: Type[BaseException], exc: BaseException,
                           tb: types.TracebackType) -> None:
        """
        Generic hook to log uncaught exceptions with the logger.
        Suitable for sys.excepthook or pytest hook usage.

        :param exc_type: Type of the exception
        :type exc_type: Type[BaseException]
        :param exc: Exception instance
        :type exc: BaseException
        :param tb: Traceback object
        :type tb: types.TracebackType
        :return: None
        """
        logger = LoggingAdapter.get_logger()
        logger.error("Uncaught exception:",
                     exc_info=(exc_type, exc, tb))
