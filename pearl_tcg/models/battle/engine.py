from __future__ import annotations

import random
from typing import TYPE_CHECKING

from pearl_tcg.models.battle.deck import build_deck
from pearl_tcg.models.battle.state import (
    DISCARDS_PER_ROUND,
    HAND_SIZE,
    MAX_DISCARD_SWAP,
    PLAYS_PER_ROUND,
    ULTIMATE_POWER,
)

if TYPE_CHECKING:
    from pearl_tcg.models.battle.character import BattleCharacter
    from pearl_tcg.models.battle.deck import ActionCard
    from pearl_tcg.models.battle.state import Boss

RESONANCE = 1.0  # flat for now - Path Resonance/combo bonuses are a later increment


class BattleRound:
    def __init__(self, roster: list[BattleCharacter], boss: Boss) -> None:
        self.roster = roster
        self.boss = boss

        self.deck: list[ActionCard] = build_deck(roster)
        self.discard_pile: list[ActionCard] = []
        self.hand: list[ActionCard] = []

        self.sp = 0
        self.discards_remaining = DISCARDS_PER_ROUND
        self.plays_remaining = PLAYS_PER_ROUND
        self.log: list[str] = []

        self._draw(HAND_SIZE)

    @property
    def is_won(self) -> bool:
        return self.boss.is_defeated

    @property
    def is_lost(self) -> bool:
        return self.plays_remaining <= 0 and not self.is_won

    def playable_cards(self) -> list[ActionCard]:
        return [card for card in self.hand if card.sp_cost <= self.sp]

    def _draw(self, count: int) -> None:
        for _ in range(count):
            if not self.deck:
                if not self.discard_pile:
                    return
                self.deck, self.discard_pile = self.discard_pile, []
                random.shuffle(self.deck)
            self.hand.append(self.deck.pop())

    def discard(self, cards: list[ActionCard]) -> str:
        if self.discards_remaining <= 0:
            msg = "No discards remaining this round."
            raise ValueError(msg)
        if not 1 <= len(cards) <= MAX_DISCARD_SWAP:
            msg = f"Must discard between 1 and {MAX_DISCARD_SWAP} cards."
            raise ValueError(msg)

        for card in cards:
            self.hand.remove(card)
            self.discard_pile.append(card)

        self.discards_remaining -= 1
        self._draw(len(cards))

        result = f"Discarded {len(cards)} card(s), {self.discards_remaining} discards left."
        self.log.append(result)
        return result

    def play(self, card: ActionCard) -> str:
        if self.plays_remaining <= 0:
            msg = "No plays remaining this round."
            raise ValueError(msg)
        if card.sp_cost > self.sp:
            msg = (
                f"Not enough SP to play {card.ability.name} (needs {card.sp_cost}, have {self.sp})."
            )
            raise ValueError(msg)

        self.hand.remove(card)
        self.discard_pile.append(card)
        self.plays_remaining -= 1
        self.sp += card.sp_generated - card.sp_cost

        character = card.owner
        character.gain_energy(card.ability.energy_gain)

        damage, is_crit = self._roll_damage(character, card.ability.power)
        self.boss.take_damage(damage)

        result = self._log_hit(character.card.name, card.ability.name, damage, is_crit)
        self.log.append(result)
        return result

    def use_ultimate(self, character: BattleCharacter) -> str:
        if not character.energy_full:
            msg = f"{character.card.name}'s Energy is not full."
            raise ValueError(msg)

        damage, is_crit = self._roll_damage(character, ULTIMATE_POWER)
        character.consume_energy()
        self.boss.take_damage(damage)

        result = self._log_hit(
            character.card.name, character.card.ultimate.name, damage, is_crit, ultimate=True
        )
        self.log.append(result)
        return result

    def _roll_damage(self, character: BattleCharacter, power: float) -> tuple[int, bool]:
        base_damage = character.card.base_atk * power
        is_crit = random.random() < character.card.crit_rate
        multiplier = (1 + character.card.crit_dmg) if is_crit else 1
        return round(base_damage * multiplier * RESONANCE), is_crit

    def _log_hit(
        self,
        character_name: str,
        ability_name: str,
        damage: int,
        is_crit: bool,
        *,
        ultimate: bool = False,
    ) -> str:
        crit_text = " (CRIT!)" if is_crit else ""
        prefix = "ULTIMATE" if ultimate else "plays"
        return (
            f"{character_name} {prefix} {ability_name}{crit_text} - {damage} DMG. "
            f"Boss HP: {self.boss.current_hp}/{self.boss.max_hp}"
        )
