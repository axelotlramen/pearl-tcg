from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pearl_tcg.enums import CardAbility

if TYPE_CHECKING:
    from pearl_tcg.models.battle.character import BattleCharacter
    from pearl_tcg.models.cards import Ability

BASIC_COPIES = 4
SKILL_COPIES = 2
TALENT_COPIES = 3

SP_COST = {
    CardAbility.BASIC: 0,
    CardAbility.SKILL: 1,
    CardAbility.TALENT: 0,
}
SP_GENERATED = {
    CardAbility.BASIC: 1,
    CardAbility.SKILL: 0,
    CardAbility.TALENT: 0,
}


@dataclass
class ActionCard:
    owner: BattleCharacter
    ability: Ability
    slot: CardAbility

    @property
    def sp_cost(self) -> int:
        return SP_COST[self.slot]

    @property
    def sp_generated(self) -> int:
        return SP_GENERATED[self.slot]

    def __repr__(self) -> str:
        return f"{self.owner.card.name} - {self.ability.name} ({self.slot.value})"


def build_deck(roster: list[BattleCharacter]) -> list[ActionCard]:
    deck: list[ActionCard] = []

    for character in roster:
        card = character.card
        deck.extend(
            ActionCard(character, card.basic, CardAbility.BASIC) for _ in range(BASIC_COPIES)
        )
        deck.extend(
            ActionCard(character, card.skill, CardAbility.SKILL) for _ in range(SKILL_COPIES)
        )
        deck.extend(
            ActionCard(character, card.talent, CardAbility.TALENT) for _ in range(TALENT_COPIES)
        )

    random.shuffle(deck)
    return deck
