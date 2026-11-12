# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Display colors for the parts of a house in the viewport."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from bld_modules import BaseWallModule, DoorModule, PostModule, StairModule, WindowModule

Color = tuple[float, float, float, float]


@dataclass(frozen=True)
class FootprintColors:
    """Display colors for the parts of a house, as linear RGBA in 0..1."""

    main: Color = (0.60, 0.85, 0.62, 1.0)
    """Color of the main building, pastel green."""
    extension: Color = (0.95, 0.60, 0.60, 1.0)
    """Color of all extensions, pastel red."""
    door: Color = (0.60, 0.75, 0.95, 1.0)
    """Color of all door modules, pastel blue."""
    window: Color = (0.98, 0.92, 0.60, 1.0)
    """Color of all window modules, pastel yellow."""
    post: Color = (0.80, 0.68, 0.92, 1.0)
    """Color of all post modules, pastel lilac."""
    stair: Color = (0.98, 0.76, 0.56, 1.0)
    """Color of all stair modules, pastel orange."""
    foundation: Color = (0.78, 0.76, 0.72, 1.0)
    """Color of the foundation, pastel stone grey."""

    def __post_init__(self) -> None:
        """Validates that every color has four channels in range.

        Raises:
            ValueError: If a color does not have four channels in 0..1.

        Returns:
            None.
        """
        for color in (self.main, self.extension, self.door, self.window, self.post, self.stair, self.foundation):
            if len(color) != 4 or not all(0.0 <= channel <= 1.0 for channel in color):
                raise ValueError(f"Invalid color {color}, expected 4 channels in 0..1")

    def color_for(self, module: BaseWallModule) -> Color | None:
        """Looks up the display color of a module.

        Args:
            module: Module to color.

        Returns:
            Door, window, post or stair color, None for modules that keep the default color.
        """
        if isinstance(module, DoorModule):
            return self.door
        if isinstance(module, WindowModule):
            return self.window
        if isinstance(module, PostModule):
            return self.post
        if isinstance(module, StairModule):
            return self.stair
        return None


footprint_colors: FootprintColors = FootprintColors()
