"""
Zero-Discord smoke test for the collection drop-and-claim system - rolls a drop, claims a card,
grinds its condition, and sells another, without needing a live bot.

Usage: uv run python -m test.drop_demo
"""

from __future__ import annotations

import random

from pearl_tcg.constants import CONDITION_UPGRADE_COST, SELL_VALUE_BY_RARITY
from pearl_tcg.enums import CardCondition
from pearl_tcg.models.game_data import GameData
from pearl_tcg.models.owned_card import compute_combat_atk
from pearl_tcg.utils.drop_rolls import roll_rarity

GUILD_ID = "test-guild"
USER_ID = "test-user"


def main() -> None:
    game_data = GameData()
    state = game_data.get_guild_drop_state(GUILD_ID)

    print("=== Rolling a 5-card drop ===")
    characters = list(game_data.cards.values())
    slots = [(random.choice(characters).name, roll_rarity(state)) for _ in range(5)]
    for name, rarity in slots:
        print(f"  {name} - {rarity}★")

    print()
    print("=== Claiming the first slot ===")
    name, rarity = slots[0]
    instance = game_data.add_owned_card(USER_ID, name, rarity)
    game_data.save_users()
    card = game_data.cards[name]
    print(
        f"Claimed {instance.character_name} ({instance.rarity}★, {instance.condition.name.title()})"
    )
    print(f"Combat ATK: {compute_combat_atk(card, instance)} (base {card.base_atk})")

    print()
    print("=== Grinding its condition up one step ===")
    user = game_data.get_user(USER_ID)
    cost = CONDITION_UPGRADE_COST[instance.condition]
    print(f"Cost from {instance.condition.name.title()}: {cost} materials (have {user.materials})")
    user.materials += 999  # pretend we ground enough materials
    instance.condition = CardCondition(instance.condition + 1)
    game_data.save_users()
    print(
        f"Now {instance.condition.name.title()} - Combat ATK: {compute_combat_atk(card, instance)}"
    )

    print()
    print("=== Claiming and selling a second card ===")
    name2, rarity2 = slots[1]
    instance2 = game_data.add_owned_card(USER_ID, name2, rarity2)
    game_data.save_users()
    sold = game_data.remove_owned_card(USER_ID, instance2.id)
    assert sold is not None
    value = SELL_VALUE_BY_RARITY[sold.rarity]
    game_data.add_currency(USER_ID, value)
    game_data.save_users()
    print(f"Sold {sold.character_name} ({sold.rarity}★) for {value} currency")

    print()
    print(f"Final owned cards: {len(user.owned_cards)}")
    print(f"Final currency: {user.currency}, materials: {user.materials}")


if __name__ == "__main__":
    main()
