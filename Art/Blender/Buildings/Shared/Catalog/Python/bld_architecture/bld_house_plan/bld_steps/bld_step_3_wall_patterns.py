# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Step 3 helper: picks the wall widths of a segment from all splits, filtered by rules."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

import itertools
import random
from collections.abc import Callable, Iterable

from bld_modules import TOLERANCE

WallPattern = tuple[float, ...]
"""Wall widths in m in walking order."""

PatternRule = Callable[[WallPattern], bool]
"""Tests one pattern, True if it is acceptable."""


def is_symmetric(pattern: WallPattern) -> bool:
    """Tests whether the pattern reads the same from both ends.

    Args:
        pattern: Wall widths in m.

    Returns:
        True if the pattern equals its reverse, otherwise False.
    """
    return pattern == pattern[::-1]


def max_neighbour_ratio(limit: float) -> PatternRule:
    """Creates a rule that limits how much wider a wall may be than its neighbour.

    Args:
        limit: Largest allowed width ratio of two neighbouring walls, e.g. 2.0.

    Returns:
        Rule that is True if no two neighbouring walls differ by more than limit.
    """

    def rule(pattern: WallPattern) -> bool:
        return all(
            max(first_width, second_width) / min(first_width, second_width) <= limit + TOLERANCE
            for first_width, second_width in itertools.pairwise(pattern)
        )

    return rule


def max_run_of(width: float, limit: int) -> PatternRule:
    """Creates a rule that limits how many walls of one width may stand in a row.

    Args:
        width: Wall width in m the rule watches.
        limit: Largest allowed number of walls of that width in a row.

    Returns:
        Rule that is True if no more than limit walls of that width follow each other.
    """

    def rule(pattern: WallPattern) -> bool:
        run_length: int = 0
        for pattern_width in pattern:
            run_length = run_length + 1 if abs(pattern_width - width) <= TOLERANCE else 0
            if run_length > limit:
                return False
        return True

    return rule


class WallPatternPicker:
    """Splits a segment length into wall widths: all splits, rules, preferences, random pick."""

    def __init__(
        self,
        widths: Iterable[float],
        rules: Iterable[PatternRule] = (),
        preferences: Iterable[PatternRule] = (is_symmetric,),
        max_extra_walls: int = 2,
    ) -> None:
        """Creates a wall pattern picker.

        Args:
            widths: Wall widths in m that may be used.
            rules: Hard filters, a pattern must pass all of them. If none does,
                the rules are ignored for that length.
            preferences: Soft filters in priority order, each one only applies
                if at least one pattern passes it.
            max_extra_walls: How many walls more than the best pattern a pattern may have
                and still be drawn from.

        Raises:
            ValueError: If no width is given, a width is not positive or max_extra_walls is negative.
        """
        width_units: set[int] = {round(width * 100) for width in widths}
        if not width_units or min(width_units) <= 0:
            raise ValueError(f"Widths must be a non-empty set of positive values, got {width_units}")
        if max_extra_walls < 0:
            raise ValueError(f"max_extra_walls must be >= 0, got {max_extra_walls}")

        self._width_units: tuple[int, ...] = tuple(sorted(width_units, reverse=True))
        self._rules: tuple[PatternRule, ...] = tuple(rules)
        self._preferences: tuple[PatternRule, ...] = tuple(preferences)
        self._max_extra_walls: int = max_extra_walls
        self._pools: dict[int, tuple[WallPattern, ...]] = {}

    def pick(self, length: float, random_source: random.Random) -> WallPattern:
        """Picks the wall widths for one segment.

        Args:
            length: Segment length in m.
            random_source: Random stream the pick is drawn from.

        Raises:
            ValueError: If the widths cannot add up to the length.

        Returns:
            Wall widths in m in walking order, adding up to the length.
        """
        length_units: int = round(length * 100)
        if length_units not in self._pools:
            self._pools[length_units] = self._build_pool(length_units)
        return random_source.choice(self._pools[length_units])

    def _build_pool(self, length_units: int) -> tuple[WallPattern, ...]:
        """Builds the patterns a segment length is drawn from.

        Args:
            length_units: Segment length in cm.

        Raises:
            ValueError: If the widths cannot add up to the length.

        Returns:
            Patterns with at most max_extra_walls more walls than the best one,
            fewest walls first, in a fixed order.
        """
        patterns: list[WallPattern] = [
            tuple(units / 100 for units in split) for split in self._splits(length_units)
        ]
        if not patterns:
            raise ValueError(
                f"No combination of {self._width_units} cm adds up to {length_units} cm"
            )

        candidates: list[WallPattern] = [
            pattern for pattern in patterns if all(rule(pattern) for rule in self._rules)
        ]
        if not candidates:
            candidates = patterns

        for preference in self._preferences:
            preferred: list[WallPattern] = [
                pattern for pattern in candidates if preference(pattern)
            ]
            if preferred:
                candidates = preferred

        candidates.sort(key=lambda pattern: (len(pattern), pattern))
        wall_limit: int = len(candidates[0]) + self._max_extra_walls
        return tuple(pattern for pattern in candidates if len(pattern) <= wall_limit)

    def _splits(self, length_units: int) -> list[tuple[int, ...]]:
        """Collects every ordered way to add up the widths to the length.

        Args:
            length_units: Length to fill in cm.

        Returns:
            All splits in cm, order counts (1+2 and 2+1 are different), empty if none fits.
        """
        splits_by_length: dict[int, list[tuple[int, ...]]] = {0: [()]}
        for current_length in range(1, length_units + 1):
            splits_by_length[current_length] = [
                (width_unit, *rest)
                for width_unit in self._width_units
                if width_unit <= current_length
                for rest in splits_by_length[current_length - width_unit]
            ]
        return splits_by_length[length_units]
