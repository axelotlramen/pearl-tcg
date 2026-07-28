from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from pearl_tcg.models.battle.marks import Mark

HAND_SIZE = 7
DISCARDS_PER_ROUND = 4
PLAYS_PER_ROUND = 4
MAX_DISCARD_SWAP = 5
MAX_COMBO_SIZE = 5

ULTIMATE_POWER = 4.0


class Boss:
    def __init__(self, name: str, max_hp: int) -> None:
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        # Generic attachable state, opaque to pearl_tcg - whatever a private combo resolver
        # wants to stash here (or not) is up to pearl_tcg_assets, not named here.
        self.marks: list[Mark] = []

    @property
    def is_defeated(self) -> bool:
        return self.current_hp <= 0

    def take_damage(self, amount: int) -> None:
        self.current_hp = max(0, self.current_hp - amount)

    def add_mark(self, mark: Mark) -> None:
        self.marks.append(mark)

    def consume_marks(self, predicate: Callable[[Mark], bool]) -> list[Mark]:
        matching = [mark for mark in self.marks if predicate(mark)]
        self.marks = [mark for mark in self.marks if not predicate(mark)]
        return matching
