from __future__ import annotations

HAND_SIZE = 7
DISCARDS_PER_ROUND = 4
PLAYS_PER_ROUND = 4
MAX_DISCARD_SWAP = 5

ULTIMATE_POWER = 4.0


class Boss:
    def __init__(self, name: str, max_hp: int) -> None:
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp

    @property
    def is_defeated(self) -> bool:
        return self.current_hp <= 0

    def take_damage(self, amount: int) -> None:
        self.current_hp = max(0, self.current_hp - amount)
