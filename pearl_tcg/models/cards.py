from __future__ import annotations

from typing import TYPE_CHECKING

from pearl_tcg.enums import AbilityType, Path

if TYPE_CHECKING:
    from pearl_tcg.enums import Element


class Ability:
    def __init__(
        self,
        name: str,
        desc: str,
        power: float,
        energy_gain: int = 20,
        type: AbilityType = AbilityType.NONE,  # noqa: A002
        path: Path | None = None,
        combo_tag: str = "",
    ) -> None:
        self.name = name
        self.desc = desc
        self.power = power
        self.energy_gain = energy_gain
        self.type = type
        # None until Card.__init__ fills it in from the owning character's Path, unless a
        # generic (non-character) card ever sets its own explicitly.
        self.path = path
        # Opaque to pearl_tcg on purpose - only pearl_tcg_assets' combo resolvers assign or
        # interpret any meaning here, so no specific mechanic is named in the open-source repo.
        self.combo_tag = combo_tag

    def __repr__(self) -> str:
        return f"{self.name}: {self.desc}"


class Card:
    path: Path

    def __init__(
        self,
        name: str,
        element: Element,
        base_atk: int,
        base_def: int,
        base_spd: int,
        crit_rate: float,
        crit_dmg: float,
        basic: Ability,
        skill: Ability,
        talent: Ability,
        ultimate: Ability,
        energy_start: int = 50,
        energy_max: int = 100,
    ) -> None:
        self.name = name
        self.element = element
        self.base_atk = base_atk
        self.base_def = base_def
        self.base_spd = base_spd
        self.crit_rate = crit_rate
        self.crit_dmg = crit_dmg
        self.basic = basic
        self.skill = skill
        self.talent = talent
        self.ultimate = ultimate
        self.energy_start = energy_start
        self.energy_max = energy_max

        for ability in (basic, skill, talent, ultimate):
            if ability.path is None:
                ability.path = self.path

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
