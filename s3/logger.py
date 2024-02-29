"""Loads a default logger with StreamHandler set to DEBUG mode.

>>> logging.Logger

"""

import logging


def default_handler() -> logging.StreamHandler:
    """Creates a ``StreamHandler`` and assigns a default format to it.

    Returns:
        logging.StreamHandler:
        Returns an instance of the ``StreamHandler`` object.
    """
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


def default_logger() -> logging.Logger:
    """Creates a default logger with debug mode enabled.

    Returns:
        logging.Logger:
        Returns an instance of the ``Logger`` object.
    """
    logger = logging.getLogger(__name__)
    logger.addHandler(hdlr=default_handler())
    logger.setLevel(level=logging.DEBUG)
    return logger
