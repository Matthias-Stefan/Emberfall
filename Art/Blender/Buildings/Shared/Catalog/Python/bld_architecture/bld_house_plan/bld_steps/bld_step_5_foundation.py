# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 5: rings with openings -> optional foundation under the outline, rings lifted onto it."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from dataclasses import replace

from ...bld_create_info import FoundationCreateInfo
from ..bld_house_plan import FoundationPlan, ModuleRing
from .bld_step_2_outline import OutlineRing


class FoundationPlanner:
    """Plans the foundation band under the outline and lifts the modules onto it."""

    def plan(
        self,
        outlines: tuple[OutlineRing, ...],
        create_info: FoundationCreateInfo,
        wall_depth: float,
    ) -> FoundationPlan | None:
        """Plans the foundation of one building.

        Args:
            outlines: Outline rings of the footprint, the foundation follows them.
            create_info: Rules for the foundation.
            wall_depth: Wall thickness in m, the band is centered on the wall midline.

        Returns:
            The foundation, None if the create info switches it off.
        """
        if not create_info.enabled:
            return None
        return FoundationPlan(
            outlines=outlines,
            height=create_info.height,
            overhang=create_info.overhang,
            wall_depth=wall_depth,
        )

    def lift(self, ring: ModuleRing, foundation: FoundationPlan | None) -> ModuleRing:
        """Raises every module of a ring onto the foundation.

        Args:
            ring: Ring of placements standing on the ground.
            foundation: Foundation to stand on, None keeps the ring on the ground.

        Returns:
            The ring with every elevation set to the foundation height.
        """
        if foundation is None:
            return ring
        return ModuleRing(
            tuple(replace(placement, elevation=foundation.height) for placement in ring.placements)
        )
