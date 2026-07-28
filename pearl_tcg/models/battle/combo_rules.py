from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pearl_tcg.models.battle.deck import ActionCard
    from pearl_tcg.models.battle.state import Boss


@dataclass(frozen=True)
class ComboEffect:
    """A single card's Resonance contribution from one resolver."""

    resonance_multiplier: float = 1.0


class ComboResolver:
    """Base class for a combo rule."""

    name: str
    # Lower runs first. Matters when one resolver's output (e.g. a Mark it adds/consumes)
    # should be visible to another resolver within the same play - order isn't left to
    # filesystem glob() ordering.
    priority: int = 100
    # combo_tag values this resolver actually interprets, so a typo'd tag on a card can be
    # flagged instead of silently doing nothing.
    recognized_tags: frozenset[str] = frozenset()

    def resolve(self, cards: list[ActionCard], boss: Boss) -> list[ComboEffect]:
        """Return a per-card ComboEffect, same length and order as `cards`."""
        raise NotImplementedError
