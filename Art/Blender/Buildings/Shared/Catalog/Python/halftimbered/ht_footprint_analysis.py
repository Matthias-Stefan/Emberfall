# Copyright (c) 2026 Emberfall. All Rights Reserved.

from halftimbered.datatypes import HtPillarKind, HtPillarPoint, HtRect, HtRectKind, HtEdge, HtEdgeAxis


def ht_kind_by_cell(rects: list[HtRect]) -> dict[tuple[int, int], HtRectKind]:
    """Maps every covered cell to its rect kind, MAIN wins on overlap.

    Args:
        rects: Footprint of the house in cells.

    Returns:
        Kind per cell.
    """
    kind_by_cell: dict[tuple[int, int], HtRectKind] = {}
    for rect in rects:
        for cell_x in range(rect.x, rect.x + rect.width):
            for cell_y in range(rect.y, rect.y + rect.depth):
                cell: tuple[int, int] = (cell_x, cell_y)
                if rect.kind == HtRectKind.MAIN or cell not in kind_by_cell:
                    kind_by_cell[cell] = rect.kind
    return kind_by_cell


def ht_find_pillar_points(rects: list[HtRect]) -> list[HtPillarPoint]:
    """Returns every grid point that needs a pillar.

    Args:
        rects: Footprint of the house in cells.

    Returns:
        Pillar points with their corner type and annex flag.
    """
    kind_by_cell: dict[tuple[int, int], HtRectKind] = ht_kind_by_cell(rects)
    points: list[HtPillarPoint] = []
    if not kind_by_cell:
        return points

    min_x: int = min(cell[0] for cell in kind_by_cell)
    max_x: int = max(cell[0] for cell in kind_by_cell)
    min_y: int = min(cell[1] for cell in kind_by_cell)
    max_y: int = max(cell[1] for cell in kind_by_cell)

    for x in range(min_x, max_x + 2):
        for y in range(min_y, max_y + 2):
            # the 4 cells around grid point (x, y)
            sw: bool = (x - 1, y - 1) in kind_by_cell
            se: bool = (x, y - 1) in kind_by_cell
            nw: bool = (x - 1, y) in kind_by_cell
            ne: bool = (x, y) in kind_by_cell
            count: int = sw + se + nw + ne

            if count == 0 or count == 4:
                continue
            if count == 2 and ((sw and ne) or (se and nw)):
                print(f"ht_find_pillar_points: corner-only contact at ({x}, {y}), skipped")
                continue

            occupied: list[HtRectKind] = [
                kind_by_cell[cell]
                for cell in ((x - 1, y - 1), (x, y - 1), (x - 1, y), (x, y))
                if cell in kind_by_cell
            ]
            annex_only: bool = all(kind == HtRectKind.ANNEX for kind in occupied)

            pillar_kind: HtPillarKind = HtPillarKind.EDGE
            if count == 1:
                pillar_kind = HtPillarKind.CONVEX
            elif count == 3:
                pillar_kind = HtPillarKind.CONCAVE
            elif occupied[0] != occupied[1]:
                # Two cells side by side with different kinds: height change
                pillar_kind = HtPillarKind.STEP

            points.append(HtPillarPoint(x, y, pillar_kind, annex_only))
    return points


def ht_find_outer_edges(rects: list[HtRect]) -> list[HtEdge]:
    """Returns every cell edge that borders an empty cell.

    Args:
        rects: Footprint of the house in cells.

    Returns:
        Outer edges with the kind of the cell they belong to.
    """
    kind_by_cell: dict[tuple[int, int], HtRectKind] = ht_kind_by_cell(rects)

    edges: list[HtEdge] = []
    for (x, y), kind in kind_by_cell.items():
        if (x, y - 1) not in kind_by_cell:
            edges.append(HtEdge(x, y, HtEdgeAxis.X, kind))
        if (x, y + 1) not in kind_by_cell:
            edges.append(HtEdge(x, y + 1, HtEdgeAxis.X, kind))
        if (x - 1, y) not in kind_by_cell:
            edges.append(HtEdge(x, y, HtEdgeAxis.Y, kind))
        if (x + 1, y) not in kind_by_cell:
            edges.append(HtEdge(x + 1, y, HtEdgeAxis.Y, kind))
    return edges