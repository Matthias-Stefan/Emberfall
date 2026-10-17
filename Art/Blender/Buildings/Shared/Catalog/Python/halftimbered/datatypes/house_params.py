# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass, field


@dataclass
class HtBaseParams:
    """Size limits of the main rect in meters.

    Attributes:
        min_width: Minimum width in meters.
        max_width: Maximum width in meters.
        min_depth: Minimum depth in meters.
        max_depth: Maximum depth in meters.
    """

    min_width: float = 6.0
    max_width: float = 8.0
    min_depth: float = 4.0
    max_depth: float = 6.0


@dataclass
class HtGroundLayerParams:
    """Settings of the stone layer at the bottom of the house.

    Attributes:
        stone_floor_chance: Chance from 0 to 1 that the ground is a whole stone floor.
        plinth_height: Height of the low plinth in meters.
        floor_height: Height of a whole stone floor in meters.
    """

    stone_floor_chance: float = 0.2
    plinth_height: float = 0.6
    floor_height: float = 2.6


@dataclass
class HtWingParams:
    """Settings for the attached wings.

    Attributes:
        max_wings: Maximum number of wings attached to the base.
        max_attempts: Re-roll limit per wing before it is skipped.
        min_wing_depth: Minimum depth of a wing in meters (perpendicular to the base edge).
        max_wing_depth: Maximum depth of a wing in meters.
        min_wing_width: Minimum width of a wing in meters (along the base edge).
        max_wing_width: Maximum width of a wing in meters.
    """

    max_wings: int = 2
    max_attempts: int = 20
    min_wing_depth: float = 4.0
    max_wing_depth: float = 6.0
    min_wing_width: float = 4.0
    max_wing_width: float = 8.0


@dataclass
class HtAnnexParams:
    """Rules for when a rect counts as an annex.

    Attributes:
        max_annex_width: Rects up to this width in meters count as annex.
        max_annex_depth: Rects up to this depth in meters count as annex.
        annex_height: Wall height of an annex in meters.
        annex_chance: Chance from 0 to 1 that a wing that qualifies becomes an annex.
    """

    max_annex_width: float = 4.0
    max_annex_depth: float = 4.0
    annex_height: float = 2.6
    annex_chance: float = 0.5


@dataclass
class HtHouseParams:
    """Everything that applies to the whole house, plus one struct per phase.

    Attributes:
        house_name: Name of the house collection.
        grid: Cell size in meters.
        offset_x: Placement of the house on X in meters.
        offset_y: Placement of the house on Y in meters.
        seed: Seed for reproducible houses, None rolls a new one.
        wall_thickness: Thickness of the stone walls in meters.
        base: Limits of the main rect.
        ground: Settings of the stone layer.
        wings: Settings of the wings.
        annex: Rules for annexes.
    """

    house_name: str = "HalfTimberedHouse"
    grid: float = 2.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    seed: int | None = None
    wall_thickness: float = 0.3
    base: HtBaseParams = field(default_factory=HtBaseParams)
    ground: HtGroundLayerParams = field(default_factory=HtGroundLayerParams)
    wings: HtWingParams = field(default_factory=HtWingParams)
    annex: HtAnnexParams = field(default_factory=HtAnnexParams)