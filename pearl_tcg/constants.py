from __future__ import annotations

from pearl_tcg.enums import CardCondition, CardRarity

EMBED_TIMEOUT = 60
TURN_TIME_LIMIT = 15

NEW_ACCOUNT_MESSAGE = (
    "You don't own any cards yet, but your Pearl TCG account has been created. "
    "Cards will be claimable soon."
)

# Multipliers applied to Card.base_atk to get an owned instance's combat ATK.
RARITY_MULTIPLIERS: dict[CardRarity, float] = {
    CardRarity.ONE_STAR: 1.0,
    CardRarity.TWO_STAR: 1.15,
    CardRarity.THREE_STAR: 1.35,
    CardRarity.FOUR_STAR: 1.6,
    CardRarity.FIVE_STAR: 2.0,
}
CONDITION_MULTIPLIERS: dict[CardCondition, float] = {
    CardCondition.DAMAGED: 0.6,
    CardCondition.POOR: 0.7,
    CardCondition.GOOD: 0.8,
    CardCondition.EXCELLENT: 0.9,
    CardCondition.MINT: 1.0,
}

# Chance a dropped card is each rarity, before pity is applied.
BASE_RARITY_RATES: dict[CardRarity, float] = {
    CardRarity.ONE_STAR: 0.50,
    CardRarity.TWO_STAR: 0.30,
    CardRarity.THREE_STAR: 0.14,
    CardRarity.FOUR_STAR: 0.05,
    CardRarity.FIVE_STAR: 0.01,
}
# Streak length (drops since the last tier-or-better hit) at which pity starts ramping, and at
# which the next drop of that tier-or-better is guaranteed. Only 3/4/5-star are pity-tracked.
PITY_SOFT_START: dict[CardRarity, int] = {
    CardRarity.THREE_STAR: 12,
    CardRarity.FOUR_STAR: 16,
    CardRarity.FIVE_STAR: 190,
}
PITY_HARD_CAP: dict[CardRarity, int] = {
    CardRarity.THREE_STAR: 18,
    CardRarity.FOUR_STAR: 25,
    CardRarity.FIVE_STAR: 230,
}

# Random range for how many messages a guild's drop channel waits before the next card drop
# spawns from chat activity.
DROP_MESSAGE_THRESHOLD_MIN = 15
DROP_MESSAGE_THRESHOLD_MAX = 25
# How long a spawned drop's claim buttons stay live before they're disabled.
DROP_CLAIM_TIMEOUT_SECONDS = 120
# Cooldowns on the manual /drop now command: how often one user can trigger it, and how often
# any drop can be triggered in the same guild regardless of who runs the command.
MANUAL_DROP_PER_USER_COOLDOWN_SECONDS = 5.0
MANUAL_DROP_PER_GUILD_COOLDOWN_SECONDS = 2.0

# Currency granted for selling an owned card, by its rarity.
SELL_VALUE_BY_RARITY: dict[CardRarity, int] = {
    CardRarity.ONE_STAR: 0,
    CardRarity.TWO_STAR: 0,
    CardRarity.THREE_STAR: 0,
    CardRarity.FOUR_STAR: 0,
    CardRarity.FIVE_STAR: 0,
}
# Materials granted for discarding an owned card, by its rarity.
DISCARD_MATERIALS_BY_RARITY: dict[CardRarity, int] = {
    CardRarity.ONE_STAR: 0,
    CardRarity.TWO_STAR: 0,
    CardRarity.THREE_STAR: 0,
    CardRarity.FOUR_STAR: 0,
    CardRarity.FIVE_STAR: 0,
}
# Materials cost to advance FROM this condition to the next one. MINT has no next step.
CONDITION_UPGRADE_COST: dict[CardCondition, int] = {
    CardCondition.DAMAGED: 0,
    CardCondition.POOR: 0,
    CardCondition.GOOD: 0,
    CardCondition.EXCELLENT: 0,
}

AVAILABLE_BORDERS = ["default"]
