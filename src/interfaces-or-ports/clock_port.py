from datetime import datetime
from typing import Protocol


class ClockPort(Protocol):
    """
    Interface for obtaining the current date and time.
    """

    def now(self) -> datetime:
        """
        Return the current timezone-aware datetime.
        """
        ...