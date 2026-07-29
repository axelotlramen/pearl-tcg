from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from pearl_tcg.models.owned_card import OwnedCard


class CardDeck(BaseModel):
    name: str = "Untitled Deck"
    # OwnedCard.id values, not character names - a slot points at a specific owned instance.
    cards: list[str] = Field(default_factory=list)


class TCGUser(BaseModel):
    owned_cards: list[OwnedCard] = Field(default_factory=list)
    decks: list[CardDeck] = Field(default_factory=list)
    active_deck_index: int = 0
    currency: int = 0
    # Spent to advance a card's condition toward Mint.
    materials: int = 0
    start_date: datetime = Field(default_factory=lambda: datetime.now(UTC))


def describe_deck(user: TCGUser, deck: CardDeck) -> str:
    """Resolve a deck's OwnedCard.id slots back into readable "Character (X★)" strings."""
    by_id = {owned.id: owned for owned in user.owned_cards}
    parts = []
    for instance_id in deck.cards:
        owned = by_id.get(instance_id)
        parts.append(f"{owned.character_name} ({owned.rarity}★)" if owned else "(missing card)")
    return ", ".join(parts)
