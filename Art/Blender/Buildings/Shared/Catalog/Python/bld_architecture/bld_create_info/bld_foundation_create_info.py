# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Create info for the optional foundation under one building."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass


@dataclass(frozen=True)
class FoundationCreateInfo:
    """Rules for the foundation, a stone band under the walls that lifts the house off the ground."""

    enabled: bool = True
    """Whether the building gets a foundation, otherwise the walls stand on the ground."""
    height: float = 0.40
    """Height of the foundation in m, the stairs in front of the doors climb this height."""
    overhang: float = 0.05
    """How far the foundation sticks out past the outer wall face in m."""

    def __post_init__(self) -> None:
        """Validates the rules right after construction.

        Raises:
            ValueError: If a value is out of range.

        Returns:
            None.
        """
        if self.height <= 0.0:
            raise ValueError(f"height must be > 0, got {self.height}")
        if self.overhang < 0.0:
            raise ValueError(f"overhang must be >= 0, got {self.overhang}")
