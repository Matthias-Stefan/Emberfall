# Copyright (c) 2026 Emberfall. All Rights Reserved.

import random

from halftimbered.datatypes import HtHouseParams, HtWallRun, HtRectKind


def ht_pick_doors(house_params: HtHouseParams, runs: list[HtWallRun],
                  rng: random.Random) -> dict[int, int]:
    """Picks the wall runs that get a door and the wall segment the door replaces.

    Args:
        house_params: Provides max_doors and chance_falloff.
        runs: Closed wall runs.
        rng: Random source of the house.

    Returns:
        Run index -> segment index inside the run (0 is the 160 start piece, so always >= 1).
        Only MAIN runs with at least 2 cells are eligible.
    """
    door_params = house_params.door
    eligible: list[int] = [
        run_index for run_index, run in enumerate(runs)
        if run.kind == HtRectKind.MAIN and run.length_cells >= 2
    ]
    rng.shuffle(eligible)

    doors: dict[int, int] = {}
    chance: float = 1.0
    for run_index in eligible:
        if len(doors) >= door_params.max_doors:
            break
        if rng.random() < chance:
            doors[run_index] = rng.randint(1, runs[run_index].length_cells - 1)
        chance *= door_params.chance_falloff
    return doors