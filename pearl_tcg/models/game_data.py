from __future__ import annotations

from durin_tcg.models.user import TCGUser
from durin_tcg.utils.reading_cards import read_cards
from durin_tcg.utils.reading_users import load_all_users, save_all_users


class GameData:
    def __init__(self) -> None:
        self.users = load_all_users()
        self.cards = read_cards()

    def save_users(self) -> None:
        save_all_users(self.users)

    def add_user(self, user_id: str) -> None:
        self.users[user_id] = TCGUser()
        self.save_users()

    def get_user(self, user_id: str) -> TCGUser:
        if user_id not in self.users:
            self.users[user_id] = TCGUser()
            self.save_users()
        return self.users[user_id]

    def add_currency(self, user_id: str, amount: int) -> None:
        self.users[user_id].currency += amount

    def add_card(self, user_id: str, card_name: str) -> None:
        if card_name not in self.users[user_id].owned_cards:
            self.users[user_id].owned_cards.append(card_name)
