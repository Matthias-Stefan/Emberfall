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


def ht_collect_cells(rects: list[HtRect]) -> set[tuple[int, int]]:
    """Returns all cells covered by the rects.

    Args:
        rects: Footprint of the house in cells.

    Returns:
        Set of (x, y) cell coordinates.
    """
    cells: set[tuple[int, int]] = set(ht_kind_by_cell(rects).keys())
    return cells


def ht_find_pillar_points(rects: list[HtRect]) -> list[HtPillarPoint]:
    """Returns every grid point that needs a pillar.

    Args:
        rects: Footprint of the house in cells.

    Returns:
        Pillar points with their corner type.
    """
    kind_by_cell: dict[tuple[int, int], HtRectKind] = ht_kind_by_cell(rects)
    cells: set[tuple[int, int]] = set(kind_by_cell.keys())
    points: list[HtPillarPoint] = []
    if not cells:
        return points

    min_x: int = min(cell[0] for cell in cells)
    max_x: int = max(cell[0] for cell in cells)
    min_y: int = min(cell[1] for cell in cells)
    max_y: int = max(cell[1] for cell in cells)

    for x in range(min_x, max_x + 2):
        for y in range(min_y, max_y + 2):
            # the 4 cells around grid point (x, y)
            sw: bool = (x - 1, y - 1) in cells
            se: bool = (x, y - 1) in cells
            nw: bool = (x - 1, y) in cells
            ne: bool = (x, y) in cells
            count: int = sw + se + nw + ne

            if count == 1:
                points.append(HtPillarPoint(x, y, HtPillarKind.CONVEX))
            elif count == 3:
                points.append(HtPillarPoint(x, y, HtPillarKind.CONCAVE))
            elif count == 2:
                if (sw and ne) or (se and nw):
                    print(f"ht_find_pillar_points: corner-only contact at ({x}, {y}), skipped")
                else:
                    # The two occupied cells sit side by side; a different kind means a height change
                    occupied: list[HtRectKind] = [
                        kind_by_cell[cell]
                        for cell in ((x - 1, y - 1), (x, y - 1), (x - 1, y), (x, y))
                        if cell in kind_by_cell
                    ]
                    pillar_kind: HtPillarKind = HtPillarKind.EDGE
                    if occupied[0] != occupied[1]:
                        pillar_kind = HtPillarKind.STEP
                    points.append(HtPillarPoint(x, y, pillar_kind))
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


def ht_point_touches_kind(point: HtPillarPoint, rects: list[HtRect], kind: HtRectKind) -> bool:
    """Checks whether a grid point lies on the corner area of a rect of the given kind.

    Args:
        point: Grid point in cells.
        rects: Footprint of the house in cells.
        kind: Rect kind to look for.

    Returns:
        True if the point lies inside or on the border of a rect of this kind.
    """
    for rect in rects:
        if rect.kind != kind:
            continue
        inside_x: bool = rect.x <= point.x <= rect.x + rect.width
        inside_y: bool = rect.y <= point.y <= rect.y + rect.depth
        if inside_x and inside_y:
            return True
    return False