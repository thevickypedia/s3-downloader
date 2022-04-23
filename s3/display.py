import inspect
import os
from datetime import datetime
from typing import Any


class Format:
    """Initiates Format object to define variables that print the message in a certain format.

    >>> Format

    """

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\x1B[3m'


class Colors:
    """Initiates Colors object to define variables that print the message in a certain color.

    >>> Colors

    """

    VIOLET = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    LIGHT_GREEN = '\033[32m'
    LIGHT_YELLOW = '\033[2;33m'
    LIGHT_RED = '\033[31m'


class Echo:
    """Initiates Echo objects to set text to certain format and color based on the level of the message.

    >>> Echo

    """

    _DATETIME_FORMAT = '%b-%d-%Y %H:%M:%S'

    def __init__(self):
        self._colors = Colors
        self._format = Format

    def _prefix(self) -> str:
        """Replicates the logging config to print colored statements accordingly.

        Returns:
            str:
            A well formatted prefix to be added before a print statement.
        """
        calling_file = inspect.stack()[2].filename.removeprefix(os.getcwd() + os.path.sep).removesuffix('.py')
        return f"{datetime.now().strftime(self._DATETIME_FORMAT)} - " \
               f"[{calling_file}:{inspect.stack()[2].lineno}] - " \
               f"{inspect.stack()[2].function} - "

    def debug(self, msg: Any) -> None:
        """Method for debug statement.

        Args:
            msg: Message to be printed.
        """
        print(f"{self._colors.LIGHT_GREEN}DEBUG{self._colors.END}:{'':<6}{self._prefix()}{msg}")

    def info(self, msg: Any) -> None:
        """Method for info statement.

        Args:
            msg: Message to be printed.
        """
        print(f"{self._colors.GREEN}INFO{self._colors.END}:{'':<7}{self._prefix()}{msg}")

    def warning(self, msg: Any) -> None:
        """Method for warning statement.

        Args:
            msg: Message to be printed.
        """
        print(f"{self._colors.YELLOW}WARNING{self._colors.END}:{'':<4}{self._prefix()}{msg}")

    def error(self, msg: Any) -> None:
        """Method for error statement.

        Args:
            msg: Message to be printed.
        """
        print(f"{self._colors.RED}ERROR{self._colors.END}:{'':<6}{self._prefix()}{msg}")

    def critical(self, msg: Any) -> None:
        """Method for critical statement.

        Args:
            msg: Message to be printed.
        """
        print(f"{self._colors.RED}{self._format.BOLD}CRITICAL{self._colors.END}:"
              f"{'':<3}{self._prefix()}{msg}")


if __name__ == '__main__':
    echo = Echo()
    echo.debug('This is a test debug message')
    echo.info('This is a test info message')
    echo.warning('This is a test warning message')
    echo.error('This is a test error message')
    echo.critical('This is a test critical message')
