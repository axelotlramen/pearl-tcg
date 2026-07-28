from __future__ import annotations

from typing import TYPE_CHECKING

from pearl_tcg.enums import Path

if TYPE_CHECKING:
    from pearl_tcg.enums import Element, Rarity


class Ability:
    def __init__(self, name: str, desc: str) -> None:
        self.name = name
        self.desc = desc

    def __repr__(self) -> str:
        return f"{self.name}: {self.desc}"


class Card:
    path: Path

    def __init__(
        self,
        name: str,
        element: Element,
        rarity: Rarity,
        base_atk: int,
        base_def: int,
        base_spd: int,
        crit_rate: float,
        crit_dmg: float,
        basic: Ability,
        skill: Ability,
        ultimate: Ability,
    ) -> None:
        self.name = name
        self.element = element
        self.rarity = rarity
        self.base_atk = base_atk
        self.base_def = base_def
        self.base_spd = base_spd
        self.crit_rate = crit_rate
        self.crit_dmg = crit_dmg
        self.basic = basic
        self.skill = skill
        self.ultimate = ultimate

    def __repr__(self) -> str:
        return f"**{self.name}** ({self.path.value} - {self.element.value})"

    def __str__(self) -> str:
        return self.__repr__()


class DestructionCard(Card):
    path = Path.DESTRUCTION


class HuntCard(Card):
    path = Path.HUNT


class EruditionCard(Card):
    path = Path.ERUDITION


class HarmonyCard(Card):
    path = Path.HARMONY


class NihilityCard(Card):
    path = Path.NIHILITY


class PreservationCard(Card):
    path = Path.PRESERVATION


class AbundanceCard(Card):
    path = Path.ABUNDANCE


class RemembranceCard(Card):
    path = Path.REMEMBRANCE


class ElationCard(Card):
    path = Path.ELATION
