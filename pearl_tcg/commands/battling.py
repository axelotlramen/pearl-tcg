from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord

from durin_tcg.models.game import AIPlayer, Battle, Character, Player
from durin_tcg.views.battling.battle_invite_view import BattleInviteView
from durin_tcg.views.battling.battle_views import AIBattleView, BattleView, PlayerBattleView

if TYPE_CHECKING:
    from durin_tcg.models.game_data import GameData


class BattleCommand:
    def __init__(
        self,
        challenger: discord.User | discord.Member,
        opponent: discord.User | Literal["AI"],
        game_data: GameData,
    ) -> None:
        self.challenger = challenger
        self.opponent = opponent
        self.game_data = game_data

    async def send_invite(self, interaction: discord.Interaction) -> None:
        view = BattleInviteView(user=self.challenger, battle_command=self)
        await view.send_summary(interaction)

    async def run_player(self) -> BattleView:
        if isinstance(self.opponent, str):
            msg = "The opponent should be an actual user, not an AI Player."
            raise TypeError(msg)
        player1 = self._get_player(self.challenger)
        player2 = self._get_player(self.opponent)
        battle = Battle(player1, player2)
        return PlayerBattleView(
            challenger=self.challenger,
            opponent=self.opponent,
            game=battle,
            game_data=self.game_data,
        )

    async def run_ai(self) -> BattleView:
        if isinstance(self.opponent, discord.User):
            msg = "The opponent should be an AI Player, not an actual user."
            raise TypeError(msg)
        player1 = self._get_player(self.challenger)
        player2 = self._generate_ai_player()
        battle = Battle(player1, player2)
        return AIBattleView(challenger=self.challenger, game=battle, game_data=self.game_data)

    def switch_deck(self, user: discord.User | discord.Member, new_deck_index: int) -> None:
        user_data = self.game_data.get_user(str(user.id))
        user_data.active_deck_index = new_deck_index
        self.game_data.save_users()

    def _get_player(self, user: discord.User | discord.Member) -> Player:
        user_data = self.game_data.get_user(str(user.id))
        deck = user_data.decks[0]
        actual_cards = [Character(self.game_data.cards[char_str]) for char_str in deck.cards]
        return Player(deck=actual_cards, active_character=actual_cards[0])

    def _generate_ai_player(self) -> AIPlayer:
        ai_deck = [
            Character(self.game_data.cards["Freminet"]),
            Character(self.game_data.cards["Wriothesley"]),
            Character(self.game_data.cards["Kaedehara Kazuha"]),
            Character(self.game_data.cards["Lycaon"]),
        ]
        return AIPlayer(deck=ai_deck, active_character=ai_deck[0])
