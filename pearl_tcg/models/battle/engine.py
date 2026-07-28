from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pearl_tcg.enums import CardAbility
from pearl_tcg.models.battle.combo_rules import ComboEffect
from pearl_tcg.models.battle.deck import ActionCard, build_deck
from pearl_tcg.models.battle.state import (
    DISCARDS_PER_ROUND,
    HAND_SIZE,
    MAX_COMBO_SIZE,
    MAX_DISCARD_SWAP,
    PLAYS_PER_ROUND,
    ULTIMATE_POWER,
)
from pearl_tcg.utils.reading_combos import read_combos

if TYPE_CHECKING:
    from pearl_tcg.models.battle.character import BattleCharacter
    from pearl_tcg.models.battle.combo_rules import ComboResolver
    from pearl_tcg.models.battle.state import Boss


@dataclass(frozen=True)
class PlayRecord:
    """One `play()`/`use_ultimate()` call, structured for later study - the human-readable
    `log` strings stay for display, this is for analysis (e.g. combo frequency, DMG-per-Play)."""

    cards: list[ActionCard] = field(default_factory=list)
    total_damage: int = 0
    log_text: str = ""


class BattleRound:
    def __init__(
        self,
        roster: list[BattleCharacter],
        boss: Boss,
        combo_resolvers: list[ComboResolver] | None = None,
    ) -> None:
        self.roster = roster
        self.boss = boss
        self.combo_resolvers = combo_resolvers if combo_resolvers is not None else read_combos()

        self.deck: list[ActionCard] = build_deck(roster)
        self.discard_pile: list[ActionCard] = []
        self.hand: list[ActionCard] = []

        self.sp = 0
        self.discards_remaining = DISCARDS_PER_ROUND
        self.plays_remaining = PLAYS_PER_ROUND
        self.log: list[str] = []
        self.play_history: list[PlayRecord] = []

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

    def play(self, cards: list[ActionCard]) -> str:
        if self.plays_remaining <= 0:
            msg = "No plays remaining this round."
            raise ValueError(msg)
        if not 1 <= len(cards) <= MAX_COMBO_SIZE:
            msg = f"Must play between 1 and {MAX_COMBO_SIZE} cards."
            raise ValueError(msg)

        running_sp = self.sp
        for card in cards:
            if card.sp_cost > running_sp:
                msg = (
                    f"Not enough SP to play {card.ability.name} "
                    f"(needs {card.sp_cost}, have {running_sp} at that point in the combo)."
                )
                raise ValueError(msg)
            running_sp += card.sp_generated - card.sp_cost

        bonuses = self._resolve_combo_bonuses(cards)

        hit_lines: list[str] = []
        total_damage = 0
        for card, bonus in zip(cards, bonuses, strict=True):
            self.hand.remove(card)
            self.discard_pile.append(card)
            self.sp += card.sp_generated - card.sp_cost

            character = card.owner
            character.gain_energy(card.ability.energy_gain)

            damage, is_crit = self._roll_damage(
                character, card.ability.power, bonus.resonance_multiplier
            )
            self.boss.take_damage(damage)
            total_damage += damage
            hit_lines.append(self._log_hit(character.card.name, card.ability.name, damage, is_crit))

        self.plays_remaining -= 1

        combo_summary = (
            f"Combo total: {total_damage} DMG. Boss HP: {self.boss.current_hp}/{self.boss.max_hp}"
        )
        result = "\n".join([*hit_lines, combo_summary])
        self.log.append(result)
        self.play_history.append(
            PlayRecord(cards=list(cards), total_damage=total_damage, log_text=result)
        )
        return result

    def use_ultimate(self, character: BattleCharacter) -> str:
        if not character.energy_full:
            msg = f"{character.card.name}'s Energy is not full."
            raise ValueError(msg)

        ultimate_card = ActionCard(character, character.card.ultimate, CardAbility.ULTIMATE)
        bonus = self._resolve_combo_bonuses([ultimate_card])[0]

        damage, is_crit = self._roll_damage(character, ULTIMATE_POWER, bonus.resonance_multiplier)
        character.consume_energy()
        self.boss.take_damage(damage)

        result = self._log_hit(
            character.card.name, ultimate_card.ability.name, damage, is_crit, ultimate=True
        )
        self.log.append(result)
        self.play_history.append(
            PlayRecord(cards=[ultimate_card], total_damage=damage, log_text=result)
        )
        return result

    def _resolve_combo_bonuses(self, cards: list[ActionCard]) -> list[ComboEffect]:
        multipliers = [1.0] * len(cards)
        for resolver in self.combo_resolvers:
            contribution = resolver.resolve(cards, self.boss)
            multipliers = [
                a * b.resonance_multiplier for a, b in zip(multipliers, contribution, strict=True)
            ]
        return [ComboEffect(resonance_multiplier=multiplier) for multiplier in multipliers]

    def _roll_damage(
        self, character: BattleCharacter, power: float, resonance: float
    ) -> tuple[int, bool]:
        base_damage = character.card.base_atk * power
        is_crit = random.random() < character.card.crit_rate
        multiplier = (1 + character.card.crit_dmg) if is_crit else 1
        return round(base_damage * multiplier * resonance), is_crit

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
