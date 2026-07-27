from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class CardDeck(BaseModel):
    name: str = "Untitled Deck"
    cards: list[str] = Field(default_factory=list)


class CardSettings(BaseModel):
    card_name: str
    card_frame: str = "default"


class TCGUser(BaseModel):
    owned_cards: list[str] = Field(default_factory=list)
    decks: list[CardDeck] = Field(default_factory=list)
    active_deck_index: int = 0
    currency: int = 0
    card_settings: list[CardSettings] = Field(default_factory=list)
    start_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    card_pity: int = 0
