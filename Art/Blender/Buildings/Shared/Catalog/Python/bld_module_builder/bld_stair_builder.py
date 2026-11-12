# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Builds the mesh of a stair module, solid block or open wooden stair, with optional handrails."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import bmesh

from bld_modules import StairModule
from .bld_base_module_builder import BaseModuleBuilder

Profile = list[tuple[float, float]]
"""Counter-clockwise outline in the Y/Z plane, Y to the right and Z up, in m."""


class StairBuilder(BaseModuleBuilder):
    """Builds a straight stair, local frame: front (-Y) is the bottom step, steps climb to +Y."""

    def __init__(
        self,
        module: StairModule,
        cheek_thickness: float = 0.20,
        cheek_height: float = 0.30,
        stringer_thickness: float = 0.08,
        stringer_depth: float = 0.12,
        tread_thickness: float = 0.04,
        rail_height: float = 0.90,
        rail_thickness: float = 0.05,
    ) -> None:
        """Creates a stair builder.

        Args:
            module: Stair module providing size, step count and variant.
            cheek_thickness: Width of the side walls of a solid stair in m.
            cheek_height: Height of the side walls above the steps in m.
            stringer_thickness: Width of the side beams of an open stair in m.
            stringer_depth: Height of the side beams below the step corners in m.
            tread_thickness: Thickness of the wooden treads of an open stair in m.
            rail_height: Height of the handrail above the step nosings in m.
            rail_thickness: Width and height of the handrail and its posts in m.

        Returns:
            None.
        """
        super().__init__(module)
        self._stair_module: StairModule = module
        self._cheek_thickness: float = cheek_thickness
        self._cheek_height: float = cheek_height
        self._stringer_thickness: float = stringer_thickness
        self._stringer_depth: float = stringer_depth
        self._tread_thickness: float = tread_thickness
        self._rail_height: float = rail_height
        self._rail_thickness: float = rail_thickness
        return None

    def build(self) -> bmesh.types.BMesh:
        """Builds the stair with the variant the module asks for.

        Returns:
            A new BMesh in m, centered in X and Y, floor at Z = 0.
            The caller owns it and must call free() on it.
        """
        bm: bmesh.types.BMesh = bmesh.new()
        if self._stair_module.solid:
            self._build_solid(bm)
        else:
            self._build_open(bm)
        if self._stair_module.has_handrail:
            self._build_handrails(bm)
        return bm

    def _nosing_height(self, y: float) -> float:
        """Computes the height of the line through all step nosings.

        Args:
            y is the position along the stair in m.

        Returns:
            Height in m of the nosing line at that position.
        """
        stair: StairModule = self._stair_module
        return stair.rise + stair.height / stair.depth * (y + stair.depth * 0.5)

    def _step_front(self, step_index: int) -> float:
        """Computes the Y of the front edge of one step.

        Args:
            step_index is the step counted from the bottom, starting at 0.

        Returns:
            Y in m of the front edge.
        """
        stair: StairModule = self._stair_module
        return -stair.depth * 0.5 + step_index * stair.tread

    def _step_profile(self, drop: float) -> Profile:
        """Builds the closed outline of the stepped block, floor to top step.

        Args:
            drop is how far the step tops are lowered in m.

        Returns:
            Counter-clockwise outline with the step tops at their height minus drop.
        """
        stair: StairModule = self._stair_module
        half_depth: float = stair.depth * 0.5
        profile: Profile = [(-half_depth, 0.0), (half_depth, 0.0), (half_depth, stair.height - drop)]
        for step_index in range(stair.step_count - 1, -1, -1):
            front: float = self._step_front(step_index)
            profile.append((front, (step_index + 1) * stair.rise - drop))
            if step_index > 0:
                profile.append((front, step_index * stair.rise - drop))
        return profile

    def _build_solid(self, bm: bmesh.types.BMesh) -> None:
        """Builds the stepped block between two sloped side walls.

        Args:
            bm is the mesh the geometry is added to.

        Returns:
            None.
        """
        stair: StairModule = self._stair_module
        half_width: float = stair.width * 0.5
        half_depth: float = stair.depth * 0.5
        cheek: float = self._cheek_thickness

        self._add_prism(bm, self._step_profile(0.0), -half_width + cheek, half_width - cheek)

        cheek_profile: Profile = [
            (-half_depth, 0.0),
            (half_depth, 0.0),
            (half_depth, stair.height + self._cheek_height),
            (-half_depth, stair.rise + self._cheek_height),
        ]
        self._add_prism(bm, cheek_profile, -half_width, -half_width + cheek)
        self._add_prism(bm, cheek_profile, half_width - cheek, half_width)
        return None

    def _build_open(self, bm: bmesh.types.BMesh) -> None:
        """Builds two saw-tooth side beams with loose treads on top, no risers.

        Args:
            bm is the mesh the geometry is added to.

        Returns:
            None.
        """
        stair: StairModule = self._stair_module
        half_width: float = stair.width * 0.5
        half_depth: float = stair.depth * 0.5
        tread: float = self._tread_thickness

        # beam underside runs parallel to the nosing line, clipped at the floor
        offset: float = stair.rise + tread + self._stringer_depth
        floor_y: float = -half_depth + (offset - stair.rise) * stair.depth / stair.height
        back_bottom: float = self._nosing_height(half_depth) - offset
        beam_profile: Profile = [(-half_depth, 0.0), (floor_y, 0.0), (half_depth, back_bottom)]
        beam_profile += self._step_profile(tread)[2:]
        beam: float = self._stringer_thickness
        self._add_prism(bm, beam_profile, -half_width, -half_width + beam)
        self._add_prism(bm, beam_profile, half_width - beam, half_width)

        for step_index in range(stair.step_count):
            front: float = self._step_front(step_index)
            top: float = (step_index + 1) * stair.rise
            tread_profile: Profile = [
                (front, top - tread),
                (front + stair.tread, top - tread),
                (front + stair.tread, top),
                (front, top),
            ]
            self._add_prism(bm, tread_profile, -half_width, half_width)
        return None

    def _build_handrails(self, bm: bmesh.types.BMesh) -> None:
        """Builds one rail with a post on every step on both sides.

        Args:
            bm is the mesh the geometry is added to.

        Returns:
            None.
        """
        stair: StairModule = self._stair_module
        half_width: float = stair.width * 0.5
        rail: float = self._rail_thickness
        side: float = self._cheek_thickness if stair.solid else self._stringer_thickness
        centre_x: float = half_width - side * 0.5

        post_centres: list[float] = [
            self._step_front(step_index) + rail * 0.5 for step_index in range(stair.step_count)
        ]
        for sign in (-1.0, 1.0):
            x_min: float = sign * centre_x - rail * 0.5
            x_max: float = sign * centre_x + rail * 0.5

            for step_index, centre_y in enumerate(post_centres):
                # sloped top and (on solid stairs) sloped base, so the rail and the surface fit flush
                back_y: float = centre_y - rail * 0.5
                front_y: float = centre_y + rail * 0.5
                post_profile: Profile = [
                    (back_y, self._post_base(step_index, back_y)),
                    (front_y, self._post_base(step_index, front_y)),
                    (front_y, self._nosing_height(front_y) + self._rail_height),
                    (back_y, self._nosing_height(back_y) + self._rail_height),
                ]
                self._add_prism(bm, post_profile, x_min, x_max)

            start_y: float = post_centres[0] - rail * 0.5
            end_y: float = post_centres[-1] + rail * 0.5
            start_z: float = self._nosing_height(start_y) + self._rail_height
            end_z: float = self._nosing_height(end_y) + self._rail_height
            rail_profile: Profile = [
                (start_y, start_z),
                (end_y, end_z),
                (end_y, end_z + rail),
                (start_y, start_z + rail),
            ]
            self._add_prism(bm, rail_profile, x_min, x_max)
        return None

    def _post_base(self, step_index: int, centre_y: float) -> float:
        """Computes the height where a handrail post starts.

        Args:
            step_index is the step the post stands on, counted from the bottom.
            centre_y is the Y of the measured point in m.

        Returns:
            Height in m of the surface the post stands on.
        """
        stair: StairModule = self._stair_module
        if stair.solid:
            slope: float = (stair.height - stair.rise) / stair.depth
            return stair.rise + self._cheek_height + slope * (centre_y + stair.depth * 0.5)
        return (step_index + 1) * stair.rise

    @staticmethod
    def _add_prism(
        bm: bmesh.types.BMesh,
        profile: Profile,
        x_min: float,
        x_max: float,
    ) -> None:
        """Extrudes a Y/Z outline along X into a closed solid with outward faces.

        Args:
            bm is the mesh the faces are added to.
            profile is the counter-clockwise outline in the Y/Z plane in m.
            x_min is the X of the left end in m.
            x_max is the X of the right end in m.

        Returns:
            None.
        """
        left: list[bmesh.types.BMVert] = [bm.verts.new((x_min, y, z)) for y, z in profile]
        right: list[bmesh.types.BMVert] = [bm.verts.new((x_max, y, z)) for y, z in profile]
        bm.faces.new(right)
        bm.faces.new(list(reversed(left)))
        count: int = len(profile)
        for index in range(count):
            following: int = (index + 1) % count
            bm.faces.new([left[index], left[following], right[following], right[index]])
        return None
