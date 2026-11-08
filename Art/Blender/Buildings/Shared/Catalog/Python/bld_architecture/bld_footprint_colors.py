# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass

Color = tuple[float, float, float, float]


@dataclass(frozen=True)
class FootprintColors:
    """Display colors for the parts of a footprint, as linear RGBA in 0..1."""

    main: Color = (0.60, 0.85, 0.62, 1.0)
    """Color of the main building, pastel green."""
    extension: Color = (0.95, 0.60, 0.60, 1.0)
    """Color of all extensions, pastel red."""

    def __post_init__(self) -> None:
        """Validates that every color has four channels in range.

        Raises:
            ValueError: If a color does not have four channels in 0..1.

        Returns:
            None.
        """
        for color in (self.main, self.extension):
            if len(color) != 4 or not all(0.0 <= channel <= 1.0 for channel in color):
                raise ValueError(f"Invalid color {color}, expected 4 channels in 0..1")
        return None


footprint_colors: FootprintColors = FootprintColors()
