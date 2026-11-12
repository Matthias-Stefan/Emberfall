# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 1: create info -> footprint, the built-up grid cells of a building."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import math
import random
from dataclasses import dataclass
from enum import Enum

from ...bld_create_info import BuildingCreateInfo


class Side(Enum):
    """Side of a rectangle in cell space, Y points up."""

    NORTH = "north"
    EAST = "east"
    SOUTH = "south"
    WEST = "west"


@dataclass(frozen=True)
class CellRectangle:
    """Axis-aligned rectangle of grid cells, bounds inclusive."""

    min_x: int
    """Smallest X cell index."""
    min_y: int
    """Smallest Y cell index."""
    max_x: int
    """Largest X cell index."""
    max_y: int
    """Largest Y cell index."""

    def __post_init__(self) -> None:
        """Validates that the rectangle has at least one cell.

        Raises:
            ValueError: If a maximum lies below its minimum.

        Returns:
            None.
        """
        if self.max_x < self.min_x or self.max_y < self.min_y:
            raise ValueError(f"Empty rectangle: {self}")
        return None

    @property
    def width(self) -> int:
        """Extent along X in cells."""
        return self.max_x - self.min_x + 1

    @property
    def depth(self) -> int:
        """Extent along Y in cells."""
        return self.max_y - self.min_y + 1

    @property
    def area(self) -> int:
        """Number of cells."""
        return self.width * self.depth

    def cells(self) -> frozenset[tuple[int, int]]:
        """Returns all cells of the rectangle.

        Returns:
            Cell indices as (x, y) tuples.
        """
        return frozenset(
            (cell_x, cell_y)
            for cell_x in range(self.min_x, self.max_x + 1)
            for cell_y in range(self.min_y, self.max_y + 1)
        )


@dataclass(frozen=True)
class Footprint:
    """Built-up grid cells of one building."""

    seed: int
    """Seed the footprint was designed with, for reproducing it."""
    main_cells: frozenset[tuple[int, int]]
    """Cells of the main building as (x, y) indices."""
    extension_cells: tuple[frozenset[tuple[int, int]], ...] = ()
    """Cells per extension, in placement order."""


class FootprintDesigner:
    """Rolls the main building and its extensions on the grid."""

    def design(self, create_info: BuildingCreateInfo) -> Footprint:
        """Designs the footprint of one building.

        Args:
            create_info: Description of the building to design.

        Raises:
            ValueError: If no main building size fits the limits.

        Returns:
            Main building and extensions as grid cells, carrying the seed.
        """
        random_source: random.Random = random.Random(create_info.seed)

        main_width, main_depth = self._roll_main_size(create_info, random_source)
        main_rectangle: CellRectangle = CellRectangle(0, 0, main_width - 1, main_depth - 1)
        extensions: list[CellRectangle] = self._place_extensions(
            create_info, random_source, main_rectangle
        )
        return Footprint(
            seed=create_info.seed,
            main_cells=main_rectangle.cells(),
            extension_cells=tuple(extension.cells() for extension in extensions),
        )

    def _roll_main_size(
        self, create_info: BuildingCreateInfo, random_source: random.Random
    ) -> tuple[int, int]:
        """Rolls width and depth of the main building in cells.

        Args:
            create_info: Limits for the building.
            random_source: The only source of randomness.

        Raises:
            ValueError: If no area in the allowed range has a fitting rectangle.

        Returns:
            Width and depth in cells.
        """
        areas: list[int] = list(
            range(create_info.min_main_area, create_info.max_main_area + 1)
        )
        random_source.shuffle(areas)

        # walk the areas in random order, the first one with a valid rectangle wins
        for area in areas:
            candidates: list[tuple[int, int]] = self._rectangles_for_area(
                area, create_info
            )
            if candidates:
                return random_source.choice(candidates)

        raise ValueError(
            f"No main building size fits the limits: areas "
            f"{create_info.min_main_area}..{create_info.max_main_area}, "
            f"min edge {create_info.footprint.min_main_edge}, "
            f"max aspect ratio {create_info.footprint.max_aspect_ratio}"
        )

    @staticmethod
    def _rectangles_for_area(
        area: int, create_info: BuildingCreateInfo
    ) -> list[tuple[int, int]]:
        """Collects all width and depth pairs that give exactly the given area.

        Args:
            area: Target area in cells.
            create_info: Limits for the edge length and aspect ratio.

        Returns:
            Valid (width, depth) pairs in ascending width order, both
            orientations included, empty if the area has none (e.g. a prime).
        """
        rectangles: list[tuple[int, int]] = []
        min_edge: int = create_info.footprint.min_main_edge

        for width in range(min_edge, area // min_edge + 1):
            if area % width != 0:
                continue
            depth: int = area // width
            if depth < min_edge:
                continue
            longer_edge: int = max(width, depth)
            shorter_edge: int = min(width, depth)
            if longer_edge / shorter_edge > create_info.footprint.max_aspect_ratio:
                continue
            rectangles.append((width, depth))
        return rectangles

    def _place_extensions(
        self,
        create_info: BuildingCreateInfo,
        random_source: random.Random,
        main_rectangle: CellRectangle,
    ) -> list[CellRectangle]:
        """Places up to extensions.max_count rectangles around the main building.

        Args:
            create_info: Limits for the extensions.
            random_source: The only source of randomness.
            main_rectangle: Main building the extensions attach to.

        Returns:
            Placed extensions in placement order, may be fewer than allowed.
        """
        extension_info = create_info.extensions
        placed: list[CellRectangle] = []
        occupied: set[tuple[int, int]] = set(main_rectangle.cells())
        total_area: int = main_rectangle.area
        max_extension_area: int = math.floor(
            main_rectangle.area * extension_info.max_area_ratio
        )

        for _ in range(extension_info.max_count):
            parents: list[CellRectangle] = (
                [main_rectangle, *placed]
                if extension_info.allow_chained
                else [main_rectangle]
            )
            area_limit: int = min(
                max_extension_area, create_info.footprint.max_total_area - total_area
            )
            extension: CellRectangle | None = self._try_place_extension(
                create_info, random_source, parents, occupied, area_limit
            )
            if extension is None:
                continue  # no luck within max_attempts, this extension is skipped
            placed.append(extension)
            occupied |= extension.cells()
            total_area += extension.area
        return placed

    def _try_place_extension(
        self,
        create_info: BuildingCreateInfo,
        random_source: random.Random,
        parents: list[CellRectangle],
        occupied: set[tuple[int, int]],
        area_limit: int,
    ) -> CellRectangle | None:
        """Tries to attach one extension within max_attempts.

        Args:
            create_info: Limits for size and attempts.
            random_source: The only source of randomness.
            parents: Rectangles the extension may attach to.
            occupied: Cells that are already built up.
            area_limit: Largest allowed extension area in cells.

        Returns:
            The placed rectangle, None if every attempt failed.
        """
        extension_info = create_info.extensions
        for _ in range(extension_info.max_attempts):
            parent: CellRectangle = random_source.choice(parents)
            side: Side = random_source.choice(list(Side))
            width: int = random_source.randint(extension_info.min_size, extension_info.max_size)
            depth: int = random_source.randint(extension_info.min_size, extension_info.max_size)
            if width * depth > area_limit:
                continue

            candidate: CellRectangle = self._attach(
                parent, side, width, depth, random_source
            )
            if candidate.cells() & occupied:
                continue
            return candidate
        return None

    @staticmethod
    def _attach(
        parent: CellRectangle,
        side: Side,
        width: int,
        depth: int,
        random_source: random.Random,
    ) -> CellRectangle:
        """Docks a rectangle to one side of the parent.

        Args:
            parent: Rectangle to attach to.
            side: Side of the parent the new rectangle sits on.
            width: Extent of the new rectangle along X in cells.
            depth: Extent of the new rectangle along Y in cells.
            random_source: Rolls where along the shared side it sits.

        Returns:
            The new rectangle, sharing at least two cells of edge with the parent
            (or the whole shorter edge if that is shorter than two).
        """
        if side in (Side.EAST, Side.WEST):
            overlap: int = min(2, depth, parent.depth)
            min_y: int = random_source.randint(
                parent.min_y - depth + overlap, parent.max_y - overlap + 1
            )
            min_x: int = parent.max_x + 1 if side is Side.EAST else parent.min_x - width
            return CellRectangle(min_x, min_y, min_x + width - 1, min_y + depth - 1)

        overlap = min(2, width, parent.width)
        min_x = random_source.randint(
            parent.min_x - width + overlap, parent.max_x - overlap + 1
        )
        min_y = parent.max_y + 1 if side is Side.NORTH else parent.min_y - depth
        return CellRectangle(min_x, min_y, min_x + width - 1, min_y + depth - 1)
