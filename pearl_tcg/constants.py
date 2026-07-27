from __future__ import annotations

from durin_tcg.enums import CardDamageType, CardElement

EMBED_TIMEOUT = 60
TURN_TIME_LIMIT = 15

CARD_BASE_HP = 10
CARD_BASIC_ATTACK = 1
CARD_SKILL_ATTACK = 3
CARD_ULTIMATE_ATTACK = 4

CARD_ELEMENT_TO_DAMAGE_TYPE = {
    # Genshin elements
    CardElement.GI_PYRO: CardDamageType.FIRE,
    CardElement.GI_HYDRO: CardDamageType.WATER,
    CardElement.GI_CRYO: CardDamageType.ICE,
    CardElement.GI_ELECTRO: CardDamageType.ELECTRICITY,
    CardElement.GI_ANEMO: CardDamageType.AIR,
    CardElement.GI_GEO: CardDamageType.PHYSICAL,
    CardElement.GI_DENDRO: CardDamageType.PLANT,
    # HSR elements
    CardElement.HSR_PHYSICAL: CardDamageType.PHYSICAL,
    CardElement.HSR_WIND: CardDamageType.AIR,
    CardElement.HSR_FIRE: CardDamageType.FIRE,
    CardElement.HSR_ICE: CardDamageType.ICE,
    CardElement.HSR_LIGHTNING: CardDamageType.ELECTRICITY,
    CardElement.HSR_IMAGINARY: CardDamageType.AURA,
    CardElement.HSR_QUANTUM: CardDamageType.AURA,
    # ZZZ elements
    CardElement.ZZZ_ELECTRIC: CardDamageType.ELECTRICITY,
    CardElement.ZZZ_ETHER: CardDamageType.AURA,
    CardElement.ZZZ_FIRE: CardDamageType.FIRE,
    CardElement.ZZZ_ICE: CardDamageType.ICE,
    CardElement.ZZZ_PHYSICAL: CardDamageType.PHYSICAL,
}
