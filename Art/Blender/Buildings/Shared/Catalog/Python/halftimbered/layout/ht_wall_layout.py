# Copyright (c) 2026 Emberfall. All Rights Reserved.

import math

from halftimbered.assets import HtAssetDef, HtAssetKind, HtAssetLayer, HtAssetCatalog
from halftimbered.datatypes import (
    HtEdge,
    HtEdgeAxis,
    HtHouseParams,
    HtPillarPoint,
    HtPlacement,
    HtRectKind,
    HtWallRun, HtSide,
)
from halftimbered.ht_globals import (
    WALL_FIRST_LENGTH_CM,
    HALF_POST_M,
    WALL_LENGTH_CM,
    WALL_FRONT_IS_PLUS_Y
)


def _edge_start(edge: HtEdge) -> int:
    """Returns the grid coordinate where an edge begins along its own axis.

    Args:
        edge: Unit edge on the grid.

    Returns:
        X for edges along X, Y for edges along Y.
    """
    return edge.x if edge.axis == HtEdgeAxis.X else edge.y


def ht_find_wall_runs(edges: list[HtEdge], corner_points: list[HtPillarPoint]) -> list[HtWallRun]:
    """Joins unit edges into runs that end on a corner pillar.

    Args:
        edges: Outer edges in cells.
        corner_points: Grid points that carry a pillar.

    Returns:
        One run per closed edge sequence, broken sequences are dropped.
    """
    pillar_cells: set[tuple[int, int]] = {(point.x, point.y) for point in corner_points}

    # Group unit edges by line: (axis, constant coordinate, outside side) -> edges
    lines: dict[tuple[HtEdgeAxis, int, HtSide], list[HtEdge]] = {}
    for edge in edges:
        constant: int = edge.y if edge.axis == HtEdgeAxis.X else edge.x
        lines.setdefault((edge.axis, constant, edge.outside), []).append(edge)

    runs: list[HtWallRun] = []
    for (axis, constant, outside), line_edges in lines.items():
        line_edges.sort(key=_edge_start)

        current: list[HtEdge] = []
        for edge in line_edges:
            if current and _edge_start(edge) != _edge_start(current[-1]) + 1:
                current = []  # gap without pillar, drop the broken run
            current.append(edge)

            end_cell: tuple[int, int] = (edge.x + 1, edge.y) if axis == HtEdgeAxis.X else (edge.x, edge.y + 1)
            if end_cell not in pillar_cells:
                continue

            runs.append(HtWallRun(axis, constant, _edge_start(current[0]), len(current),
                                  current[0].kind, outside))
            current = []
    return runs


def _wall_rotation(axis: HtEdgeAxis, outside: HtSide) -> float:
    """Returns the Z rotation that makes the stone side face outwards.

    Args:
        axis: Direction the run goes along.
        outside: Side of the run where the outside lies.

    Returns:
        Rotation around Z in radians.
    """
    if axis == HtEdgeAxis.X:
        angle: float = 0.0 if outside == HtSide.NEGATIVE else math.pi
    else:
        angle = -math.pi / 2 if outside == HtSide.NEGATIVE else math.pi / 2

    if WALL_FRONT_IS_PLUS_Y:
        angle += math.pi
    return angle


def ht_plan_walls(house_params: HtHouseParams, runs: list[HtWallRun], catalog: HtAssetCatalog,
                  main_height_cm: int, annex_height_cm: int) -> list[HtPlacement]:
    """Fills every run with one 160 wall followed by 200 walls, butt-jointed.

    Args:
        house_params: Provides grid.
        runs: Closed wall runs.
        catalog: Catalog the walls are taken from.
        main_height_cm: Wall height for main runs.
        annex_height_cm: Wall height for annex runs.

    Returns:
        One placement per wall, positions in meters relative to the house origin.
    """
    grid: float = house_params.grid
    placements: list[HtPlacement] = []

    for run in runs:
        height_cm: int = annex_height_cm if run.kind == HtRectKind.ANNEX else main_height_cm
        lengths_cm: list[int] = [WALL_FIRST_LENGTH_CM] + [WALL_LENGTH_CM] * (run.length_cells - 1)
        rotation_z: float = _wall_rotation(run.axis, run.outside)

        cursor: float = run.start * grid + HALF_POST_M
        for length_cm in lengths_cm:
            length_m: float = length_cm / 100.0
            asset: HtAssetDef | None = catalog.first(
                kind=HtAssetKind.WALL, layer=HtAssetLayer.FOUNDATION,
                length_cm=length_cm, height_cm=height_cm)
            if asset is not None:
                center: float = cursor + length_m * 0.5
                if run.axis == HtEdgeAxis.X:
                    placements.append(HtPlacement(asset, center, run.constant * grid, rotation_z=rotation_z))
                else:
                    placements.append(HtPlacement(asset, run.constant * grid, center, rotation_z=rotation_z))
            cursor += length_m
    return placements