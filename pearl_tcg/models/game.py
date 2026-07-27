from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from durin_tcg.constants import CARD_BASE_HP
from durin_tcg.enums import CardAbility, CardDamageType, CardElement

if TYPE_CHECKING:
    from durin_tcg.models.cards import Card


class Character:
    def __init__(self, card: Card, current_hp: int = CARD_BASE_HP) -> None:
        self.card = card
        self.current_hp = current_hp
        self.current_shield: int = 0
        self.afflicted_elements: list[CardDamageType] = []

        self.final_hp: int = self.current_hp + self.current_shield

    def afflict_element(self, element: CardDamageType) -> None:
        self.afflicted_elements.append(element)


class Item(ABC):
    def __init__(self, name: str, effect_desc: str) -> None:
        self.name = name
        self.effect_desc = effect_desc

    @abstractmethod
    def effect(self) -> None:
        pass


class Player:
    def __init__(
        self,
        deck: list[Character],
        active_character: Character,
        items: list[Item] | None = None,
        action_points: int = 5,
    ) -> None:
        self.deck = deck
        self.active_character = active_character
        self.items = items
        self.action_points = action_points

    def switch_character(self, ally_id: int) -> None:
        if self.deck[ally_id] != self.active_character:
            self.active_character = self.deck[ally_id]

    def use_ability(self, ability: CardAbility, enemy: Player) -> None:
        ability_method = {
            CardAbility.BASIC: self.active_character.card.basic,
            CardAbility.SKILL: self.active_character.card.skill,
            CardAbility.ULTIMATE: self.active_character.card.ultimate,
        }.get(ability)

        if ability_method is None:
            msg = f"Unknown ability type: {ability}"
            raise ValueError(msg)

        ability_method.use(allies=self.deck, enemy=enemy)


class AIPlayer(Player):
    def choose_ability(self) -> CardAbility:
        return random.choice([CardAbility.BASIC, CardAbility.SKILL, CardAbility.ULTIMATE])

    def choose_character_switch(self) -> int | None:
        # TODO: implement logic to decide if and which character to switch to
        return None


class Battle:
    def __init__(self, player1: Player, player2: Player) -> None:
        self.player1 = player1
        self.player2 = player2
        self.player1_turn = True

    def play_game(self) -> str:
        log: list[str] = []

        while (
            self.player1.active_character.current_hp > 0
            and self.player2.active_character.current_hp > 0
        ):
            attacker = self.player1 if self.player1_turn else self.player2
            defender = self.player2 if self.player1_turn else self.player1

            log.append(
                f"{attacker.active_character.card.name} uses Basic Attack on {defender.active_character.card.name}!"
            )
            attacker.use_ability(CardAbility.ULTIMATE, defender)

            # Check if defender is defeated
            if defender.active_character.current_hp <= 0:
                log.append(f"{defender.active_character.card.name} has been defeated!")
                break

            self.player1_turn = not self.player1_turn

        winner = self.player1 if self.player1.active_character.current_hp > 0 else self.player2
        log.append(f"🏆 {winner.active_character.card.name}'s team wins!")

        return "\n".join(log)
