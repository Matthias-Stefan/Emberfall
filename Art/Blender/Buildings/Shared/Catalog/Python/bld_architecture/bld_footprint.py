# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass


@dataclass(frozen=True)
class Footprint:
    """Built-up grid cells of one building."""

    seed: int
    """Seed the footprint was designed with, for reproducing it."""
    main_cells: frozenset[tuple[int, int]]
    """Cells of the main building as (x, y) indices."""
    extension_cells: tuple[frozenset[tuple[int, int]], ...] = ()
    """Cells per extension, in placement order."""
