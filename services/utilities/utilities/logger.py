"""App level logger utility."""

import logging
import os
from typing import ClassVar

from dotenv import load_dotenv

load_dotenv()


class GetAppLogger:
    """Get Application Logger to manage logging.

    App logger precedence:
    1. Retrieve logger name from environment variable `APP_NAME`. Return singleton instance of app logger.
    2. If `APP_NAME` is not set, use the provided `fallback_name` parameter to create a new logger instance.
       2.1. If `fallback_name` is not provided, default to "default" as the logger name and return a new instance.
    """

    APP_LOGGER_INSTANCE: ClassVar[logging.Logger | None] = None

    def __init__(
        self,
        fallback_name: str = "default",
        console_log_level: int = logging.INFO,
        file_log_level: int = logging.DEBUG,
        log_file_path: str = "app.log",
    ):
        """Initialize the GetAppLogger instance.

        Warning: The app logger is made available as a singleton instance. Only one instance of the logger will be
        created throughout the application lifecycle. If you attempt to create multiple instances without specifying a
        name, the first instance will be used for all subsequent calls.

        Args:
            fallback_name (str): Fallback name for the logger if `APP_NAME` is not set. Defaults to "default".
            console_log_level (int): Log level for console output. Defaults to logging.INFO. Precedence is given to the
                                     `CONSOLE_LOG_LEVEL` environment variable if set.
            file_log_level (int): Log level for file output. Defaults to logging.DEBUG. Precedence is given to the
                                  `FILE_LOG_LEVEL` environment variable if set.
            log_file_path (str): Path to the log file. Defaults to 'app.log'. When `APP_NAME` is set, it will be
                                 overridden to `<APP_NAME>.log`.

        Examples:
            >>> import os
            >>> from utilities.logger import AppLogger
            # Module Logger
            >>> logger = AppLogger(fallback_name="my_app").get_logger()
            >>> logger.info("This is an info message.")
            2025-10-04 21:40:45,939 - my_app - INFO - This is an info message.
            # App Logger Singleton (APP_NAME not set and fallback_name not provided, defaults to 'default')
            >>> default_logger = AppLogger().get_logger()
            >>> default_logger.info("This is an info message.")
            2025-10-04 21:40:45,939 - default - INFO - This is an info message.
            # App Logger Singleton (APP_NAME set to 'bella')
            >>> os.environ["APP_NAME"] = "bella"
            >>> os.environ["CONSOLE_LOG_LEVEL"] = "INFO"
            >>> os.environ["FILE_LOG_LEVEL"] = "DEBUG"
            >>> bella_logger = AppLogger().get_logger()
            >>> bella_logger.info("This is an info message from bella.")
            2025-10-04 21:40:45,939 - bella - INFO - This is an info message from bella.
        """
        self._logger = None
        self._name = os.getenv("APP_NAME", fallback_name)
        self._console_log_level = os.getenv("CONSOLE_LOG_LEVEL", console_log_level)
        self._file_log_level = os.getenv("FILE_LOG_LEVEL", file_log_level)
        if os.getenv("APP_NAME", None) is not None:
            self._log_file_path = f"{self._name}.log"
        else:
            self._log_file_path = log_file_path

        # Default Settings
        self._DEFAULT_ROOT_LOG_LEVEL = logging.DEBUG
        self._LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Initialize logger based on APP_NAME presence
        # If APP_NAME is set, return singleton instance
        if os.getenv("APP_NAME", None) is not None:
            # Singleton pattern: Only one instance of the app logger
            if GetAppLogger.APP_LOGGER_INSTANCE is None:
                GetAppLogger.APP_LOGGER_INSTANCE = self._get_logger()
            self._logger = GetAppLogger.APP_LOGGER_INSTANCE
        else:
            # If APP_NAME is not set, create a new logger instance with the provided fallback_name
            self._logger = self._get_logger()

    def _configure_logger(self):
        """Configure the logger settings."""
        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(self._DEFAULT_ROOT_LOG_LEVEL)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(self._LOG_FORMAT)

        # Remove existing handlers to avoid duplicate logs
        for handler in self._logger.handlers:
            self._logger.removeHandler(handler)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self._console_log_level)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        # Create file handler
        file_handler = logging.FileHandler(self._log_file_path, encoding="utf-8")
        file_handler.setLevel(self._file_log_level)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def _get_logger(self):
        """Get the configured logger instance."""
        self._configure_logger()
        return self._logger

    def get_logger(self):
        """Return the logger instance."""
        return self._logger


if __name__ == "__main__":
    # Example usage
    APP_NAME_IN_ENV = False  # Change to True to test APP_NAME from environment

    if APP_NAME_IN_ENV:
        os.environ["APP_NAME"] = "bella"
        os.environ["CONSOLE_LOG_LEVEL"] = "INFO"
        os.environ["FILE_LOG_LEVEL"] = "DEBUG"
    else:
        os.environ.pop("APP_NAME")

    logger1 = GetAppLogger(fallback_name="logger1").get_logger()
    logger1.debug("This is a debug message from logger1.")
    logger1.info("This is an info message from logger1.")

    logger2 = GetAppLogger(fallback_name="logger2").get_logger()
    logger2.debug("This is a debug message from logger2.")
    logger2.info("This is an info message from logger2.")

    logger3 = GetAppLogger().get_logger()
    logger3.debug("This is a debug message from logger3.")
    logger3.info("This is an info message from logger3.")
