"""Loads a default logger with StreamHandler set to DEBUG mode.

>>> logging.Logger

"""

import logging
import os.path
import time
from enum import Enum
from typing import Union


class LogType(Enum):
    """Defines the type of logging output.

    >>> LogType

    """

    file: str = "file"
    stdout: str = "stdout"


def default_handler(log_type: LogType) -> Union[logging.StreamHandler, logging.FileHandler]:
    """Creates a handler and assigns a default format to it.

    Args:
        log_type: An instance of the ``LogType`` enum to specify the type of logging output.

    Returns:
        Union[logging.StreamHandler, logging.FileHandler]:
        Returns an instance of either ``StreamHandler`` or ``FileHandler`` based on the specified log type.
    """
    if log_type == LogType.file:
        os.makedirs("logs", exist_ok=True)
        logfile = os.path.join("logs", f"s3_downloader_{time.strftime('%Y-%m-%d_%H:%M:%S')}.log")
        handler = logging.FileHandler(filename=logfile)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(fmt=default_format())
    return handler


def default_format() -> logging.Formatter:
    """Creates a logging ``Formatter`` with a custom message and datetime format.

    Returns:
        logging.Formatter:
        Returns an instance of the ``Formatter`` object.
    """
    return logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(funcName)s - %(message)s',
        datefmt='%b-%d-%Y %I:%M:%S %p'
    )


def default_logger(log_type: LogType) -> logging.Logger:
    """Creates a default logger with debug mode enabled.

    Args:
        log_type: An instance of the ``LogType`` enum to specify the type of logging output.

    Returns:
        logging.Logger:
        Returns an instance of the ``Logger`` object.
    """
    logger = logging.getLogger(__name__)
    logger.addHandler(hdlr=default_handler(log_type))
    logger.setLevel(level=logging.DEBUG)
    return logger
