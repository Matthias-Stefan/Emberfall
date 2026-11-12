# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Create info for the extensions attached to the main building."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtensionsCreateInfo:
    """Rules for the extensions attached to the main building."""

    max_count: int = 0
    """Maximum number of extensions, 0 builds the main building only."""
    max_attempts: int = 20
    """Placement attempts per extension before it is skipped."""
    min_size: int = 3
    """Smallest extension edge length in cells."""
    max_size: int = 5
    """Largest extension edge length in cells."""
    max_area_ratio: float = 0.5
    """Extension area divided by main building area, upper limit."""
    allow_chained: bool = False
    """Whether extensions may attach to other extensions."""

    def __post_init__(self) -> None:
        """Validates the rules right after construction.

        Raises:
            ValueError: If a value is out of range or contradicts another.

        Returns:
            None.
        """
        if self.max_count < 0:
            raise ValueError(f"max_count must be >= 0, got {self.max_count}")
        if self.max_count > 0 and self.max_attempts < 1:
            raise ValueError(
                f"max_attempts must be >= 1 when extensions are allowed, got {self.max_attempts}"
            )
        if self.min_size < 1:
            raise ValueError(f"min_size must be >= 1, got {self.min_size}")
        if self.min_size > self.max_size:
            raise ValueError(f"min_size ({self.min_size}) exceeds max_size ({self.max_size})")
        if self.max_area_ratio <= 0.0:
            raise ValueError(f"max_area_ratio must be > 0, got {self.max_area_ratio}")
