# Copyright (c) 2026 Emberfall. All Rights Reserved.

# exec(bpy.data.texts["main.py"].as_string())

import sys
from pathlib import Path

import bpy

PYTHON_DIR: Path = Path(bpy.path.abspath("//")) / "Python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.append(str(PYTHON_DIR))

for name in list(sys.modules):
    if name.startswith("halftimbered"):
        del sys.modules[name]

from halftimbered import datatypes, ht_house_builder

seed: int | None = None
if datatypes.USE_TEST_SEEDS:
    index: int = bpy.app.driver_namespace.get("ht_seed_index", 0) % len(datatypes.HT_TEST_SEEDS)
    bpy.app.driver_namespace["ht_seed_index"] = index + 1
    test_seed: datatypes.HtTestSeed = datatypes.HT_TEST_SEEDS[index]
    seed = test_seed.seed
    print(f"main: test seed '{test_seed.name}' ({test_seed.seed}) - {test_seed.note}")

params: datatypes.HtHouseParams = datatypes.HtHouseParams(
    house_name="HalfTimberedHouse",
    grid=2.0,
    offset_x=10.0,
    offset_y=10.0,
    seed=seed,
    base=datatypes.HtBaseParams(
        min_width=6.0,
        max_width=8.0,
        min_depth=4.0,
        max_depth=6.0,
    ),
    ground=datatypes.HtGroundLayerParams(
        stone_floor_chance=1.0,  # NOTE: no PLINTH
        plinth_height=0.6,
        floor_height=2.6,
    ),
    wings=datatypes.HtWingParams(
        max_wings=2,
        max_attempts=20,
        min_wing_depth=4.0,
        max_wing_depth=6.0,
        min_wing_width=4.0,
        max_wing_width=8.0,
    ),
    annex=datatypes.HtAnnexParams(
        max_annex_width=6.0,
        max_annex_depth=6.0,
        annex_height=2.2,
        annex_chance=0.75,
    ),
)
ht_house_builder.ht_build_house(params)
