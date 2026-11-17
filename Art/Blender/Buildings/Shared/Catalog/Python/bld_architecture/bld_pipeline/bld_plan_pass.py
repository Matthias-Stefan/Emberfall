# Copyright (c) 2026 Emberfall. All Rights Reserved.
"""Interfaces of the passes, one pass is one step of planning."""

__author__ = "Matthias Stefan"
__version__ = "0.1.0"

from abc import ABC, abstractmethod

from .bld_drafts import HouseDraft, LevelDraft


class HousePass(ABC):
    """One step that plans part of the ground floor, the architect runs them in a fixed order."""

    @abstractmethod
    def apply(self, draft: HouseDraft) -> None:
        """Fills its part of the draft.

        Args:
            draft is the house, filled by all passes before this one.

        Returns:
            None.
        """


class LevelPass(ABC):
    """One step that plans part of a level above the ground floor, run once per level."""

    @abstractmethod
    def apply(self, draft: LevelDraft) -> None:
        """Fills its part of the draft.

        Args:
            draft is the level, filled by all passes before this one.

        Returns:
            None.
        """
