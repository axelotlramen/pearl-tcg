"""
Zero-Discord smoke test for the Increment 2 battle loop - run directly to see a full round
resolve, mirroring how the pre-rebuild codebase's Battle.play_game() worked for debugging.

Usage: uv run python -m test.battle_demo
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from pearl_tcg.models.battle.character import BattleCharacter
from pearl_tcg.models.battle.engine import BattleRound
from pearl_tcg.models.battle.state import MAX_COMBO_SIZE, Boss
from pearl_tcg.utils.reading_cards import read_cards

if TYPE_CHECKING:
    from pearl_tcg.models.battle.deck import ActionCard

TEAM = ["Mydei", "Tribbie", "Cipher", "The Herta"]
BOSS_HP = 500

# Below this, a hand's best playable option is "just a Basic" - worth burning a discard to fish
# for something better before spending one of our 4 precious Plays on it, unless we're out of
# discards anyway.
WEAK_HAND_POWER_THRESHOLD = 1.0


def _combo_is_affordable(sp: int, cards: list[ActionCard]) -> bool:
    running_sp = sp
    for card in cards:
        if card.sp_cost > running_sp:
            return False
        running_sp += card.sp_generated - card.sp_cost
    return True


def _select_combo(battle: BattleRound) -> list[ActionCard] | None:
    playable = battle.playable_cards()
    if not playable:
        return None

    # Prefer submitting same-Path cards together to trigger Path Resonance, rather than always
    # playing one card at a time - that's the whole point of Increment 2.
    by_path = defaultdict(list)
    for card in playable:
        by_path[card.ability.path].append(card)

    largest_group = max(by_path.values(), key=len)
    if len(largest_group) >= 2:
        candidate = sorted(largest_group, key=lambda c: c.ability.power, reverse=True)
        candidate = candidate[:MAX_COMBO_SIZE]
        if _combo_is_affordable(battle.sp, candidate):
            return candidate

    # Otherwise fall back to whoever's closest to a full Energy bar, power as the tiebreak.
    single_best = max(playable, key=lambda c: (c.owner.energy, c.ability.power))
    return [single_best]


def _take_turn(battle: BattleRound) -> None:
    for character in battle.roster:
        if character.energy_full:
            print(battle.use_ultimate(character))
            return

    combo = _select_combo(battle)
    combo_is_weak = (
        combo is None or max(c.ability.power for c in combo) <= WEAK_HAND_POWER_THRESHOLD
    )

    if combo_is_weak and battle.discards_remaining > 0:
        weakest_first = sorted(battle.hand, key=lambda c: c.ability.power)
        to_discard = weakest_first[:5]
        print(battle.discard(to_discard))
        return

    if combo is not None:
        print(battle.play(combo))
        return

    print("Stalled: no playable cards and no discards remaining.")
    battle.plays_remaining = 0  # force the round to end rather than loop forever


def main() -> None:
    cards = read_cards()
    roster = [BattleCharacter(cards[name]) for name in TEAM]
    boss = Boss(name="Test Dummy", max_hp=BOSS_HP)
    battle = BattleRound(roster, boss)

    print(f"=== {boss.name} ({boss.max_hp} HP) vs. {', '.join(TEAM)} ===")
    while not battle.is_won and not battle.is_lost:
        _take_turn(battle)

    print()
    print("WON" if battle.is_won else "LOST", f"- {battle.plays_remaining} plays remaining")

    print()
    print(f"=== Play History ({len(battle.play_history)} plays) ===")
    for index, record in enumerate(battle.play_history, start=1):
        names = ", ".join(f"{c.owner.card.name} {c.ability.name}" for c in record.cards)
        print(f"{index}. [{names}] -> {record.total_damage} DMG")


if __name__ == "__main__":
    main()
