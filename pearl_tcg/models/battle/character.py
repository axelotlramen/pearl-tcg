from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pearl_tcg.models.cards import Card


class BattleCharacter:
    def __init__(self, card: Card) -> None:
        self.card = card
        self.energy = card.energy_start

    @property
    def energy_full(self) -> bool:
        return self.energy >= self.card.energy_max

    def gain_energy(self, amount: int) -> None:
        self.energy = min(self.energy + amount, self.card.energy_max)

    def consume_energy(self) -> None:
        self.energy = 0
