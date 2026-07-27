from __future__ import annotations

from enum import StrEnum


class Game(StrEnum):
    GENSHIN = "Genshin Impact"
    HSR = "Honkai: Star Rail"
    ZZZ = "Zenless Zone Zero"


class CardAbility(StrEnum):
    BASIC = "Basic"
    SKILL = "Skill"
    ULTIMATE = "Ultimate"


class CardElement(StrEnum):
    # Genshin Elements
    GI_PYRO = "Pyro"
    GI_HYDRO = "Hydro"
    GI_CRYO = "Cryo"
    GI_ELECTRO = "Electro"
    GI_ANEMO = "Anemo"
    GI_GEO = "Geo"
    GI_DENDRO = "Dendro"

    # HSR Elements
    HSR_PHYSICAL = "Physical"
    HSR_WIND = "Wind"
    HSR_FIRE = "Fire"
    HSR_ICE = "Ice"
    HSR_LIGHTNING = "Lightning"
    HSR_IMAGINARY = "Imaginary"
    HSR_QUANTUM = "Quantum"

    # ZZZ Elements
    ZZZ_ELECTRIC = "Electric"
    ZZZ_ETHER = "Ether"
    ZZZ_FIRE = "Fire"
    ZZZ_ICE = "Ice"
    ZZZ_PHYSICAL = "Physical"


class CardDamageType(StrEnum):
    FIRE = "Fire"
    WATER = "Water"
    ICE = "Ice"
    ELECTRICITY = "Electricity"
    AIR = "Air"
    PLANT = "Plant"
    AURA = "Aura"
    PHYSICAL = "Physical"
