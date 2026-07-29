from __future__ import annotations

from typing import TYPE_CHECKING

from pearl_tcg.models.guild_drop_state import GuildDropState
from pearl_tcg.models.owned_card import OwnedCard
from pearl_tcg.models.user import TCGUser
from pearl_tcg.utils.reading_cards import read_cards
from pearl_tcg.utils.reading_guild_drop_state import (
    load_all_guild_drop_states,
    save_all_guild_drop_states,
)
from pearl_tcg.utils.reading_users import load_all_users, save_all_users

if TYPE_CHECKING:
    from pearl_tcg.enums import CardRarity


class GameData:
    def __init__(self) -> None:
        self.users = load_all_users()
        self.cards = read_cards()
        self.guild_drop_states = load_all_guild_drop_states()

    def save_users(self) -> None:
        save_all_users(self.users)

    def save_guild_drop_states(self) -> None:
        save_all_guild_drop_states(self.guild_drop_states)

    def add_user(self, user_id: str) -> None:
        self.users[user_id] = TCGUser()
        self.save_users()

    def get_user(self, user_id: str) -> TCGUser:
        if user_id not in self.users:
            self.users[user_id] = TCGUser()
            self.save_users()
        return self.users[user_id]

    def get_or_create_user(self, user_id: str) -> tuple[TCGUser, bool]:
        """Like `get_user`, but also reports whether this call just created the account."""
        is_new = user_id not in self.users
        return self.get_user(user_id), is_new

    def get_guild_drop_state(self, guild_id: str) -> GuildDropState:
        if guild_id not in self.guild_drop_states:
            self.guild_drop_states[guild_id] = GuildDropState()
            self.save_guild_drop_states()
        return self.guild_drop_states[guild_id]

    def add_currency(self, user_id: str, amount: int) -> None:
        self.get_user(user_id).currency += amount

    def add_owned_card(self, user_id: str, character_name: str, rarity: CardRarity) -> OwnedCard:
        instance = OwnedCard(character_name=character_name, rarity=rarity)
        self.get_user(user_id).owned_cards.append(instance)
        return instance

    def get_owned_card(self, user_id: str, instance_id: str) -> OwnedCard | None:
        return next((c for c in self.get_user(user_id).owned_cards if c.id == instance_id), None)

    def remove_owned_card(self, user_id: str, instance_id: str) -> OwnedCard | None:
        """Removes the instance and purges any deck slot referencing it."""
        instance = self.get_owned_card(user_id, instance_id)
        if instance is None:
            return None

        user = self.get_user(user_id)
        user.owned_cards.remove(instance)
        for deck in user.decks:
            deck.cards = [cid for cid in deck.cards if cid != instance_id]
        return instance
