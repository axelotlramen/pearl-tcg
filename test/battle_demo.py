"""
Zero-Discord smoke test for the Increment 1 battle loop - run directly to see a full round
resolve, mirroring how the pre-rebuild codebase's Battle.play_game() worked for debugging.

Usage: uv run python -m test.battle_demo
"""

from __future__ import annotations

from pearl_tcg.models.battle.character import BattleCharacter
from pearl_tcg.models.battle.engine import BattleRound
from pearl_tcg.models.battle.state import Boss
from pearl_tcg.utils.reading_cards import read_cards

TEAM = ["Mydei", "Tribbie", "Cipher", "The Herta"]
BOSS_HP = 500

# Below this, a hand's best playable option is "just a Basic" - worth burning a discard to fish
# for something better before spending one of our 4 precious Plays on it, unless we're out of
# discards anyway.
WEAK_HAND_POWER_THRESHOLD = 1.0


def _take_turn(battle: BattleRound) -> None:
    for character in battle.roster:
        if character.energy_full:
            print(battle.use_ultimate(character))
            return

    # Prefer whoever's closest to a full Energy bar first, so the team actually tries to cross
    # the Ultimate threshold instead of just spreading plays evenly - power is only the tiebreak.
    playable = battle.playable_cards()
    best = max(playable, key=lambda c: (c.owner.energy, c.ability.power)) if playable else None

    hand_is_weak = best is None or best.ability.power <= WEAK_HAND_POWER_THRESHOLD
    if hand_is_weak and battle.discards_remaining > 0:
        weakest_first = sorted(battle.hand, key=lambda c: c.ability.power)
        to_discard = weakest_first[:5]
        print(battle.discard(to_discard))
        return

    if best is not None:
        print(battle.play(best))
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


if __name__ == "__main__":
    main()
