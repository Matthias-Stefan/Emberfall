# Copyright (c) 2026 Emberfall. All Rights Reserved.

import math
import random

from halftimbered.datatypes import (
    HtAnnexParams,
    HtBaseParams,
    HtHouseParams,
    HtRect,
    HtRectKind,
    HtWingParams,
)


def ht_is_annex_candidate(rect: HtRect, house_params: HtHouseParams) -> bool:
    """Checks whether a rect is small enough to become an annex.

    Args:
        rect: Wing rect in cells.
        house_params: Provides grid and the annex limits in meters.

    Returns:
        True if width and depth are within the annex limits.
    """
    annex: HtAnnexParams = house_params.annex
    width_m: float = rect.width * house_params.grid
    depth_m: float = rect.depth * house_params.grid
    return width_m <= annex.max_annex_width and depth_m <= annex.max_annex_depth


def ht_rects_overlap(a: HtRect, b: HtRect) -> bool:
    """Checks whether two rects share at least one cell.

    Args:
        a: First rect.
        b: Second rect.

    Returns:
        True if the rects overlap.
    """
    overlap_x: bool = a.x < b.x + b.width and b.x < a.x + a.width
    overlap_y: bool = a.y < b.y + b.depth and b.y < a.y + a.depth
    return overlap_x and overlap_y


def ht_roll_base_rect(house_params: HtHouseParams, rng: random.Random) -> HtRect | None:
    """Rolls the base rect in cells so its size in meters stays inside [min, max].

    Args:
        house_params: Provides grid and base limits; min is rounded up, max is rounded down.

    Returns:
        The base rect at cell (0, 0), or None if no whole module count fits the limits.
    """
    base: HtBaseParams = house_params.base
    grid: float = house_params.grid

    min_width_cells: int = math.ceil(base.min_width / grid)
    max_width_cells: int = math.floor(base.max_width / grid)
    min_depth_cells: int = math.ceil(base.min_depth / grid)
    max_depth_cells: int = math.floor(base.max_depth / grid)

    if min_width_cells < 1 or min_width_cells > max_width_cells:
        print(f"ht_roll_base_rect: no module count fits width {base.min_width}-{base.max_width} m")
        return None
    if min_depth_cells < 1 or min_depth_cells > max_depth_cells:
        print(f"ht_roll_base_rect: no module count fits depth {base.min_depth}-{base.max_depth} m")
        return None

    depth_cells: int = rng.randint(min_depth_cells, max_depth_cells)
    width_cells: int = rng.randint(min_width_cells, max_width_cells)

    base_rect: HtRect = HtRect(0, 0, width_cells, depth_cells)
    return base_rect


def ht_roll_wing(base_rect: HtRect, house_params: HtHouseParams, rng: random.Random) -> HtRect | None:
    """Rolls one wing candidate on the north or south edge of the base rect.

    Args:
        base_rect: Rect the wing is attached to.
        house_params: Provides grid and the wing limits in meters.

    Returns:
        The wing candidate, not yet checked for collisions, or None if no whole
        module count fits the limits.
    """
    wings: HtWingParams = house_params.wings
    grid: float = house_params.grid

    min_depth_cells: int = math.ceil(wings.min_wing_depth / grid)
    max_depth_cells: int = math.floor(wings.max_wing_depth / grid)
    min_width_cells: int = math.ceil(wings.min_wing_width / grid)
    max_width_cells: int = math.floor(wings.max_wing_width / grid)

    if min_depth_cells < 1 or min_depth_cells > max_depth_cells:
        print(f"ht_roll_wing: no module count fits depth {wings.min_wing_depth}-{wings.max_wing_depth} m")
        return None
    if min_width_cells < 1 or min_width_cells > max_width_cells:
        print(f"ht_roll_wing: no module count fits width {wings.min_wing_width}-{wings.max_wing_width} m")
        return None

    depth_cells: int = rng.randint(min_depth_cells, max_depth_cells)
    width_cells: int = rng.randint(min_width_cells, max_width_cells)

    # Coin flip: north edge or south edge of the base
    wing_y: int = base_rect.y + base_rect.depth
    if rng.random() < 0.5:
        wing_y = base_rect.y - depth_cells

    # Start range guarantees at least 1 cell of contact with the base edge
    min_x: int = base_rect.x - width_cells + 1
    max_x: int = base_rect.x + base_rect.width - 1
    wing_x: int = rng.randint(min_x, max_x)

    wing_rect: HtRect = HtRect(wing_x, wing_y, width_cells, depth_cells)
    return wing_rect


def ht_roll_wings(base_rect: HtRect, house_params: HtHouseParams, rng: random.Random) -> list[HtRect]:
    """Rolls up to max_wings wings, each with at most max_attempts tries.

    Args:
        base_rect: Main rect of the house.
        house_params: Provides max_wings and max_attempts.

    Returns:
        The wings that found a free spot.
    """
    wings: list[HtRect] = []
    all_rects: list[HtRect] = [base_rect]

    for _ in range(house_params.wings.max_wings):
        for _ in range(house_params.wings.max_attempts):
            candidate: HtRect | None = ht_roll_wing(base_rect, house_params, rng)
            if candidate is None:
                # Limits can never fit, more attempts are pointless
                return wings

            if any(ht_rects_overlap(candidate, rect) for rect in all_rects):
                continue

            if ht_is_annex_candidate(candidate, house_params) and rng.random() < house_params.annex.annex_chance:
                candidate.kind = HtRectKind.ANNEX

            wings.append(candidate)
            all_rects.append(candidate)
            break
        else:
            print("ht_roll_wings: no free spot for wing, skipped")
    return wings