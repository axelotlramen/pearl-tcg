from __future__ import annotations

import random
from typing import TYPE_CHECKING

from pearl_tcg.constants import BASE_RARITY_RATES, PITY_HARD_CAP, PITY_SOFT_START
from pearl_tcg.enums import CardRarity

if TYPE_CHECKING:
    from pearl_tcg.models.guild_drop_state import GuildDropState

# Highest tier first - each is conditional on not already hitting a higher one this draw.
_PITY_TRACKED_TIERS = (CardRarity.FIVE_STAR, CardRarity.FOUR_STAR, CardRarity.THREE_STAR)

_STREAK_FIELD = {
    CardRarity.FIVE_STAR: "streak_5star",
    CardRarity.FOUR_STAR: "streak_4star",
    CardRarity.THREE_STAR: "streak_3star",
}


def _pity_adjusted_rate(streak: int, base_rate: float, soft_start: int, hard_cap: int) -> float:
    if streak >= hard_cap - 1:
        return 1.0
    if streak >= soft_start:
        progress = (streak - soft_start) / (hard_cap - soft_start)
        return base_rate + progress * (1.0 - base_rate)
    return base_rate


def roll_rarity(state: GuildDropState) -> CardRarity:
    """Roll one card's rarity: check 5-star first, then 4-star, then 3-star, each only if the
    higher tiers above it missed, then split whatever probability is left between 2-star and
    1-star. Updates `state`'s pity streaks based on the result before returning."""
    remaining = 1.0
    rarity: CardRarity | None = None

    for tier in _PITY_TRACKED_TIERS:
        streak = getattr(state, _STREAK_FIELD[tier])
        rate = _pity_adjusted_rate(
            streak, BASE_RARITY_RATES[tier], PITY_SOFT_START[tier], PITY_HARD_CAP[tier]
        )
        rate = min(rate, remaining)

        if random.random() < rate:
            rarity = tier
            break
        remaining -= rate

    if rarity is None:
        one_star = BASE_RARITY_RATES[CardRarity.ONE_STAR]
        two_star = BASE_RARITY_RATES[CardRarity.TWO_STAR]
        two_star_share = two_star / (one_star + two_star)
        rarity = CardRarity.TWO_STAR if random.random() < two_star_share else CardRarity.ONE_STAR

    _update_pity(state, rarity)
    return rarity


def _update_pity(state: GuildDropState, rarity: CardRarity) -> None:
    for tier in _PITY_TRACKED_TIERS:
        field = _STREAK_FIELD[tier]
        if rarity >= tier:
            setattr(state, field, 0)
        else:
            setattr(state, field, getattr(state, field) + 1)
