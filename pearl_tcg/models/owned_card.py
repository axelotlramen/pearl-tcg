from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from pearl_tcg.constants import CONDITION_MULTIPLIERS, RARITY_MULTIPLIERS
from pearl_tcg.enums import CardCondition, CardRarity

if TYPE_CHECKING:
    from pearl_tcg.models.cards import Card


class OwnedCard(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    # Name of the character this card is - not checked against the current roster, so a
    # renamed or removed character doesn't stop the record from loading.
    character_name: str
    rarity: CardRarity
    condition: CardCondition = CardCondition.DAMAGED
    border: str = "default"
    obtained_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


def compute_combat_atk(card: Card, instance: OwnedCard) -> int:
    return round(
        card.base_atk
        * RARITY_MULTIPLIERS[instance.rarity]
        * CONDITION_MULTIPLIERS[instance.condition]
    )
