from __future__ import annotations

from enum import StrEnum


class CardAbility(StrEnum):
    BASIC = "Basic"
    SKILL = "Skill"
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


class Rarity(StrEnum):
    COMMON = "Common"
    RARE = "Rare"
    LEGENDARY = "Legendary"
