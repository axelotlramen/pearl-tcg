from __future__ import annotations

from pearl_tcg.enums import Element, Path, Rarity


class Ability:
    def __init__(self, name: str, desc: str) -> None:
        self.name = name
        self.desc = desc

    def __repr__(self) -> str:
        return f"{self.name}: {self.desc}"


class Card:
    def __init__(
        self,
        name: str,
        path: Path,
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
        self.path = path
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
        super().__init__(
            name=name,
            path=Path.DESTRUCTION,
            element=element,
            rarity=rarity,
            base_atk=base_atk,
            base_def=base_def,
            base_spd=base_spd,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            basic=basic,
            skill=skill,
            ultimate=ultimate,
        )


class HuntCard(Card):
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
        super().__init__(
            name=name,
            path=Path.HUNT,
            element=element,
            rarity=rarity,
            base_atk=base_atk,
            base_def=base_def,
            base_spd=base_spd,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            basic=basic,
            skill=skill,
            ultimate=ultimate,
        )


class EruditionCard(Card):
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
        super().__init__(
            name=name,
            path=Path.ERUDITION,
            element=element,
            rarity=rarity,
            base_atk=base_atk,
            base_def=base_def,
            base_spd=base_spd,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            basic=basic,
            skill=skill,
            ultimate=ultimate,
        )


class HarmonyCard(Card):
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
        super().__init__(
            name=name,
            path=Path.HARMONY,
            element=element,
            rarity=rarity,
            base_atk=base_atk,
            base_def=base_def,
            base_spd=base_spd,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            basic=basic,
            skill=skill,
            ultimate=ultimate,
        )


class NihilityCard(Card):
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
        super().__init__(
            name=name,
            path=Path.NIHILITY,
            element=element,
            rarity=rarity,
            base_atk=base_atk,
            base_def=base_def,
            base_spd=base_spd,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            basic=basic,
            skill=skill,
            ultimate=ultimate,
        )


class PreservationCard(Card):
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
        super().__init__(
            name=name,
            path=Path.PRESERVATION,
            element=element,
            rarity=rarity,
            base_atk=base_atk,
            base_def=base_def,
            base_spd=base_spd,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            basic=basic,
            skill=skill,
            ultimate=ultimate,
        )


class AbundanceCard(Card):
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
        super().__init__(
            name=name,
            path=Path.ABUNDANCE,
            element=element,
            rarity=rarity,
            base_atk=base_atk,
            base_def=base_def,
            base_spd=base_spd,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            basic=basic,
            skill=skill,
            ultimate=ultimate,
        )


class RemembranceCard(Card):
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
        super().__init__(
            name=name,
            path=Path.REMEMBRANCE,
            element=element,
            rarity=rarity,
            base_atk=base_atk,
            base_def=base_def,
            base_spd=base_spd,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            basic=basic,
            skill=skill,
            ultimate=ultimate,
        )


class ElationCard(Card):
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
        super().__init__(
            name=name,
            path=Path.ELATION,
            element=element,
            rarity=rarity,
            base_atk=base_atk,
            base_def=base_def,
            base_spd=base_spd,
            crit_rate=crit_rate,
            crit_dmg=crit_dmg,
            basic=basic,
            skill=skill,
            ultimate=ultimate,
        )
