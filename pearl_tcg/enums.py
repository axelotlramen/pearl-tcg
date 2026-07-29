from __future__ import annotations

from enum import IntEnum, StrEnum


class CardAbility(StrEnum):
    BASIC = "Basic"
    SKILL = "Skill"
    TALENT = "Talent"
    ULTIMATE = "Ultimate"


class Element(StrEnum):
    PHYSICAL = "Physical"
    FIRE = "Fire"
    ICE = "Ice"
    LIGHTNING = "Lightning"
    WIND = "Wind"
    QUANTUM = "Quantum"
    IMAGINARY = "Imaginary"


class Path(StrEnum):
    DESTRUCTION = "Destruction"
    HUNT = "Hunt"
    ERUDITION = "Erudition"
    HARMONY = "Harmony"
    NIHILITY = "Nihility"
    PRESERVATION = "Preservation"
    ABUNDANCE = "Abundance"
    REMEMBRANCE = "Remembrance"
    ELATION = "Elation"


class AbilityType(StrEnum):
    NONE = "None"
    DEBUFF = "Debuff"
    BUFF = "Buff"
    SUMMON = "Summon"


class CardRarity(IntEnum):
    """An owned card instance's rarity, 1 to 5 stars. Ordered so tiers can be compared directly
    (e.g. `rarity >= CardRarity.FOUR_STAR`)."""

    ONE_STAR = 1
    TWO_STAR = 2
    THREE_STAR = 3
    FOUR_STAR = 4
    FIVE_STAR = 5


class CardCondition(IntEnum):
    """An owned card instance's condition, from Damaged to Mint. Ordered so a condition can be
    advanced with `CardCondition(condition + 1)` and compared directly."""

    DAMAGED = 1
    POOR = 2
    GOOD = 3
    EXCELLENT = 4
    MINT = 5
