# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Create infos and seeds the testbed builds its house grid from."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import dataclass

from bld_architecture import (
    BuildingCreateInfo,
    ExtensionsCreateInfo,
    FootprintCreateInfo,
    OpeningCreateInfo,
)


@dataclass(frozen=True)
class HouseSet:
    """Create infos and seeds the testbed builds houses from."""

    create_infos: tuple[BuildingCreateInfo, ...]
    """Base create infos, one row of houses each, their seed is replaced per house."""
    fixed_seeds: tuple[int, ...] = (1, 2, 3)
    """Seeds every row is built with each run, for reproducible comparison."""
    random_seed_count: int = 2
    """Random seeds rolled per row and run."""


default_house_set: HouseSet = HouseSet(
    create_infos=(
        # small: no extensions, few windows
        BuildingCreateInfo(
            footprint=FootprintCreateInfo(
                min_total_area=20,
                max_total_area=36,
                min_main_edge=3,
                max_aspect_ratio=1.5,
            ),
            openings=OpeningCreateInfo(window_chance=0.3),
            seed=0,
        ),
        # standard: two extensions
        BuildingCreateInfo(
            footprint=FootprintCreateInfo(
                min_total_area=48,
                max_total_area=110,
                min_main_edge=4,
                max_aspect_ratio=1.8,
            ),
            extensions=ExtensionsCreateInfo(
                max_count=2,
                max_attempts=20,
                min_size=3,
                max_size=5,
                max_area_ratio=0.5,
            ),
            seed=0,
        ),
        # long: stretched main building
        BuildingCreateInfo(
            footprint=FootprintCreateInfo(
                min_total_area=48,
                max_total_area=80,
                min_main_edge=4,
                max_aspect_ratio=2.5,
            ),
            extensions=ExtensionsCreateInfo(
                max_count=2,
                max_attempts=20,
                min_size=3,
                max_size=5,
                max_area_ratio=0.5,
            ),
            seed=0,
        ),
        # large: three chained extensions, two doors, many windows
        BuildingCreateInfo(
            footprint=FootprintCreateInfo(
                min_total_area=100,
                max_total_area=180,
                min_main_edge=6,
                max_aspect_ratio=1.6,
            ),
            extensions=ExtensionsCreateInfo(
                max_count=3,
                max_attempts=30,
                min_size=3,
                max_size=6,
                max_area_ratio=0.4,
                allow_chained=True,
            ),
            openings=OpeningCreateInfo(door_count=2, window_chance=0.7),
            seed=0,
        ),
        # compact: almost square
        BuildingCreateInfo(
            footprint=FootprintCreateInfo(
                min_total_area=36,
                max_total_area=64,
                min_main_edge=5,
                max_aspect_ratio=1.2,
            ),
            extensions=ExtensionsCreateInfo(
                max_count=1,
                max_attempts=10,
                min_size=3,
                max_size=4,
                max_area_ratio=0.3,
            ),
            seed=0,
        ),
    ),
)
