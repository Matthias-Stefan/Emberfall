# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 8: footprint and foundation -> floor slabs on every cell of the ground floor."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from bld_modules import TOLERANCE, FloorModule

from ...bld_style import ModuleAtlas
from ..bld_house_plan import FoundationPlan, ModulePlacement
from .bld_step_1_footprint import Footprint

CELL_SIZE: float = 1.0
"""Edge length of one grid cell in m, the floor slab of a whole cell has this size."""


class FloorPlanner:
    """Lays one floor slab per footprint cell, top flush with the top of the foundation."""

    def __init__(self, atlas: ModuleAtlas) -> None:
        """Creates a floor planner.

        Args:
            atlas: Floor modules the planner may lay, it needs one slab of a whole cell.

        Returns:
            None.
        """
        self._atlas: ModuleAtlas = atlas
        return None

    def plan(
        self, footprint: Footprint, foundation: FoundationPlan | None
    ) -> tuple[ModulePlacement, ...]:
        """Plans the floor of the ground level.

        Args:
            footprint: Footprint whose cells get a slab.
            foundation: Foundation the floor lies on, None means the house stands on the ground
                and needs no slab.

        Returns:
            One placement per cell in cell order, empty if there is no foundation or no slab
            of a whole cell in the atlas.
        """
        if foundation is None:
            return ()
        slab: FloorModule | None = self._find_cell_slab()
        if slab is None:
            return ()

        # the slab hangs down from the floor level, so its top is flush with the foundation top
        elevation: float = foundation.height - slab.height
        cells: frozenset[tuple[int, int]] = footprint.main_cells.union(*footprint.extension_cells)
        return tuple(
            ModulePlacement(
                slab, (cell_x + CELL_SIZE * 0.5, cell_y + CELL_SIZE * 0.5), 0, elevation
            )
            for cell_x, cell_y in sorted(cells)
        )

    def _find_cell_slab(self) -> FloorModule | None:
        """Finds the slab that covers exactly one grid cell.

        Returns:
            The slab, None if the atlas has none.
        """
        for module in self._atlas.modules_of(FloorModule):
            if (
                isinstance(module, FloorModule)
                and abs(module.width - CELL_SIZE) <= TOLERANCE
                and abs(module.depth - CELL_SIZE) <= TOLERANCE
            ):
                return module
        return None
