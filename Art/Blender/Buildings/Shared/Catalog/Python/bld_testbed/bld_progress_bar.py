# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Text progress bar for the console, one line per step."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import time


class ProgressBar:
    """Prints a progress line per step with a bar, percentage, elapsed time and estimated time left.

    One line per step on purpose: the Blender Python console cannot redraw a line in place.
    """

    def __init__(self, label: str, total: int, width: int = 24) -> None:
        """Creates a progress bar and starts its clock.

        Args:
            label: Name of the work, printed in front of the bar.
            total: Number of steps the work has.
            width: Number of characters of the bar itself.

        Returns:
            None.
        """
        self._label: str = label
        self._total: int = max(total, 1)
        self._width: int = width
        self._done: int = 0
        self._start: float = time.perf_counter()
        return None

    def advance(self, message: str = "") -> None:
        """Counts one finished step and prints the progress line.

        Args:
            message: Short text that is appended to the line, e.g. what was just built.

        Returns:
            None.
        """
        self._done = min(self._done + 1, self._total)
        elapsed: float = time.perf_counter() - self._start
        remaining: float = elapsed / self._done * (self._total - self._done)
        filled: int = round(self._width * self._done / self._total)
        bar: str = "#" * filled + "-" * (self._width - filled)
        percent: int = round(100 * self._done / self._total)
        print(
            f"{self._label} [{bar}] {self._done:>{len(str(self._total))}}/{self._total} "
            f"{percent:>3}% | {elapsed:5.1f}s elapsed, ~{remaining:5.1f}s left"
            + (f" | {message}" if message else ""),
            flush=True,
        )
        return None
