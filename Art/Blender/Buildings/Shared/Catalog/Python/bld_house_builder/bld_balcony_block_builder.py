# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the solid stone block that carries a balcony."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_architecture import BalconyPlan, FoundationPlan, Side

Cell = tuple[int, int]

# outward unit direction per side, Y points up in cell space
_OUTWARD: dict[Side, Cell] = {
    Side.NORTH: (0, 1),
    Side.EAST: (1, 0),
    Side.SOUTH: (0, -1),
    Side.WEST: (-1, 0),
}


class BalconyBlockBuilder:
    """Builds a solid stone block under the cells of a balcony, its top is the balcony floor.

    The block starts at the outer edge of the foundation band, so it never reaches into the wall
    or the door. At the ends of its wall it ends flush with the foundation, past an outer corner
    and short of an inner corner.
    """

    def __init__(
        self,
        balcony: BalconyPlan,
        foundation: FoundationPlan,
        built_cells: frozenset[Cell],
    ) -> None:
        """Creates a balcony block builder.

        Args:
            balcony: Balcony whose cells the block covers, they have to form a full rectangle.
            foundation: Foundation the block continues, provides height, wall depth and overhang.
            built_cells: Cells of the footprint, tell where the walls end.

        Raises:
            ValueError: If the cells of the balcony are not a full rectangle.

        Returns:
            None.
        """
        cells: frozenset[Cell] = balcony.cells
        cell_xs: list[int] = [cell_x for cell_x, _ in cells]
        cell_ys: list[int] = [cell_y for _, cell_y in cells]
        bounds: dict[str, float] = {
            "min_x": float(min(cell_xs)),
            "max_x": float(max(cell_xs) + 1),
            "min_y": float(min(cell_ys)),
            "max_y": float(max(cell_ys) + 1),
        }
        if (bounds["max_x"] - bounds["min_x"]) * (bounds["max_y"] - bounds["min_y"]) != len(cells):
            raise ValueError(f"Balcony cells are not a rectangle: {sorted(cells)}")

        inset: float = foundation.wall_depth * 0.5 + foundation.overhang
        outward: Cell = _OUTWARD[balcony.outward]
        inward: Cell = (-outward[0], -outward[1])

        # the wall side starts at the outer edge of the foundation band
        if outward == (0, -1):
            bounds["max_y"] -= inset
        elif outward == (0, 1):
            bounds["min_y"] += inset
        elif outward == (1, 0):
            bounds["min_x"] += inset
        else:
            bounds["max_x"] -= inset

        # the two sides along the wall follow the foundation corners
        for lateral in ((outward[1], outward[0]), (-outward[1], -outward[0])):
            edge_cells: list[Cell] = [
                cell
                for cell in cells
                if (cell[0] + lateral[0], cell[1] + lateral[1]) not in cells
                and (cell[0] + inward[0], cell[1] + inward[1]) in built_cells
            ]
            if not edge_cells:
                continue  # the wall does not reach this side of the balcony
            wall_cell: Cell = edge_cells[0]
            neighbor: Cell = (wall_cell[0] + lateral[0], wall_cell[1] + lateral[1])
            behind_neighbor: Cell = (neighbor[0] + inward[0], neighbor[1] + inward[1])
            if neighbor in built_cells:
                shift: float = -inset  # inner corner, stop at the face of the other wall
            elif behind_neighbor not in built_cells:
                shift = inset  # outer corner, reach as far as the foundation corner
            else:
                continue  # the wall goes on, the balcony simply ends mid wall
            key: str = ("max_" if lateral[0] + lateral[1] > 0 else "min_") + (
                "x" if lateral[0] != 0 else "y"
            )
            bounds[key] += shift * (lateral[0] + lateral[1])

        self._bounds: dict[str, float] = bounds
        self._height: float = foundation.height
        return None

    def build(self) -> bmesh.types.BMesh:
        """Builds the block as one closed box.

        Returns:
            A new BMesh in m, bottom at Z = 0.
            The caller owns it and must call free() on it.
        """
        bm: bmesh.types.BMesh = bmesh.new()
        created: dict = bmesh.ops.create_cube(bm, size=1.0)
        corners: list[bmesh.types.BMVert] = created["verts"]
        bmesh.ops.scale(
            bm,
            vec=(
                self._bounds["max_x"] - self._bounds["min_x"],
                self._bounds["max_y"] - self._bounds["min_y"],
                self._height,
            ),
            verts=corners,
        )
        bmesh.ops.translate(
            bm,
            vec=(
                (self._bounds["min_x"] + self._bounds["max_x"]) * 0.5,
                (self._bounds["min_y"] + self._bounds["max_y"]) * 0.5,
                self._height * 0.5,
            ),
            verts=corners,
        )
        return bm
