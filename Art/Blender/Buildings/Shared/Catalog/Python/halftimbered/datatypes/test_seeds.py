# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass


@dataclass
class HtTestSeed:
    """A known seed that produces an interesting house.

    Attributes:
        name: Short label of the case.
        seed: Seed value.
        note: Params the seed was found with, it only reproduces with these.
    """

    name: str
    seed: int
    note: str = ""


HT_TEST_SEEDS: list[HtTestSeed] = [
    HtTestSeed("seed_1", 800405,
               "max_annex 6.0x6.0, annex_chance 0.75, annex_height 2.2"),
    HtTestSeed("seed_2", 257447,
               "max_annex 6.0x6.0, annex_chance 0.75, annex_height 2.2"),
    HtTestSeed("seed_3", 279546,
               "max_annex 6.0x6.0, annex_chance 0.75, annex_height 2.2"),
]

USE_TEST_SEEDS: bool = True