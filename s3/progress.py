import threading

from alive_progress import alive_bar


class ProgressPercentage:
    """Tracks the file transfer progress in S3 and updates the alive_bar.

    >>> ProgressPercentage

    """

    def __init__(self, filename: str, size: int, bar: alive_bar):
        """Initializes the progress tracker.

        Args:
            filename: Name of the file being transferred.
            size: Total size of the file in bytes.
            bar: alive_bar instance to update progress.
        """
        self._filename = filename
        self._size = size
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._bar = bar

    def __call__(self, bytes_amount: int) -> None:
        """Callback method to update progress.

        Args:
            bytes_amount: Number of bytes transferred in the last chunk.
        """
        with self._lock:
            self._seen_so_far += bytes_amount
            percent = (self._seen_so_far / self._size) * 100
            bar_len = 20
            filled = int(bar_len * percent / 100)
            bar_str = "█" * filled + "." * (bar_len - filled)
            self._bar.text(f" || {self._filename} [{bar_str}] {percent:.0f}%")
