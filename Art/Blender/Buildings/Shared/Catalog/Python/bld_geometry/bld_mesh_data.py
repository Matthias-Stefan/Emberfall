# Copyright (c) 2026 Emberfall. All Rights Reserved.

from dataclasses import dataclass, field


@dataclass
class MeshData:
    """Plain geometry container without any bpy dependency."""

    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    """Vertex positions in m."""
    faces: list[tuple[int, ...]] = field(default_factory=list)
    """Faces as vertex index tuples, counter-clockwise seen from outside."""

    def add_box(
        self,
        min_corner: tuple[float, float, float],
        max_corner: tuple[float, float, float],
    ) -> None:
        """Appends an axis-aligned box.

        Args:
            min_corner: Corner with the smallest X, Y and Z in m.
            max_corner: Corner with the largest X, Y and Z in m.

        Returns:
            None.
        """
        min_x, min_y, min_z = min_corner
        max_x, max_y, max_z = max_corner
        first_index: int = len(self.vertices)

        self.vertices.extend([
            (min_x, min_y, min_z),  # 0 bottom, front left
            (max_x, min_y, min_z),  # 1 bottom, front right
            (max_x, max_y, min_z),  # 2 bottom, back right
            (min_x, max_y, min_z),  # 3 bottom, back left
            (min_x, min_y, max_z),  # 4 top, front left
            (max_x, min_y, max_z),  # 5 top, front right
            (max_x, max_y, max_z),  # 6 top, back right
            (min_x, max_y, max_z),  # 7 top, back left
        ])

        for face in (
            (0, 3, 2, 1),  # bottom (-Z)
            (4, 5, 6, 7),  # top (+Z)
            (0, 1, 5, 4),  # front (-Y)
            (1, 2, 6, 5),  # right (+X)
            (2, 3, 7, 6),  # back (+Y)
            (3, 0, 4, 7),  # left (-X)
        ):
            self.faces.append(tuple(first_index + index for index in face))
        return None

    def add_quad(
        self,
        corner_a: tuple[float, float, float],
        corner_b: tuple[float, float, float],
        corner_c: tuple[float, float, float],
        corner_d: tuple[float, float, float],
    ) -> None:
        """Appends one quad.

        Args:
            corner_a: First corner in m.
            corner_b: Second corner in m, counter-clockwise seen from outside.
            corner_c: Third corner in m.
            corner_d: Fourth corner in m.

        Returns:
            None.
        """
        first_index: int = len(self.vertices)
        self.vertices.extend([corner_a, corner_b, corner_c, corner_d])
        self.faces.append((first_index, first_index + 1, first_index + 2, first_index + 3))
        return None
