# Copyright (c) 2026 Emberfall. All Rights Reserved.

# Hard-wired values. Everything here should eventually move somewhere else,
# the comment above each group says where.

# Blender scene: becomes a parameter of main.py / HtHouseParams
CATALOG_COLLECTION: str = "HalfTimberedCollection"

# Generator dice rule: belongs into HtWingParams (south_chance)
WING_SOUTH_CHANCE: float = 0.5

# Post facts: come from the asset catalog (post width)
POST_WIDTH_CM: int = 40
HALF_POST_M: float = POST_WIDTH_CM / 200.0

# Wall facts: come from the asset catalog (available wall lengths, solver)
WALL_LENGTH_CM: int = 200
WALL_FIRST_LENGTH_CM: int = WALL_LENGTH_CM - POST_WIDTH_CM

# Heights of main and annex: come from the asset catalog (available heights)
MAIN_HEIGHT_CM: int = 260
ANNEX_HEIGHT_CM: int = 220