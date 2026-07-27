from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Embed, Interaction
from discord.ui import Button

from durin_tcg.constants import EMBED_TIMEOUT
from durin_tcg.views.base import BaseView
from durin_tcg.views.battling.switch_deck_view import SwitchDeckView

if TYPE_CHECKING:
    from durin_tcg.commands.battling import BattleCommand
    from durin_tcg.models.user import CardDeck


class BattleInviteView(BaseView):
    def __init__(
        self,
        user: discord.User | discord.Member,
        battle_command: BattleCommand,
        timeout: float = EMBED_TIMEOUT,
    ) -> None:
        super().__init__(timeout=timeout)

        self.user = user
        self.battle_command = battle_command

        self.selected_deck_index = self._get_selected_deck_index()
        self.selected_deck = self._get_selected_deck()

        self.message: discord.Message | None = None

        self.add_item(SwitchDeckButton())
        self.add_item(SendInviteButton())

    def _get_selected_deck_index(self) -> int:
        return self.battle_command.game_data.get_user(str(self.user.id)).active_deck_index

    def _get_selected_deck(self) -> CardDeck:
        return self.battle_command.game_data.get_user(str(self.user.id)).decks[
            self.selected_deck_index
        ]

    async def send_summary(self, interaction: Interaction) -> None:
        opponent_name = (
            self.battle_command.opponent
            if isinstance(self.battle_command.opponent, str)
            else self.battle_command.opponent.display_name
        )

        card_list = "\n".join(f"• {card}" for card in self.selected_deck.cards)

        embed = Embed(
            title="Battle Invitation",
            description=(f"**Opponent:** {opponent_name}\n**Your Deck:**\n{card_list}"),
            color=discord.Color.blurple(),
        )

        try:
            await interaction.response.send_message(embed=embed, view=self)
            self.message = await interaction.original_response()
        except discord.InteractionResponded:
            await interaction.followup.send(embed=embed, view=self)
            self.message = await interaction.original_response()


class SwitchDeckButton(Button):
    def __init__(self) -> None:
        super().__init__(label="Switch Deck", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        view: BattleInviteView = self.view  # pyright: ignore[reportAssignmentType]

        switch_view = SwitchDeckView(
            user=view.user,
            selected_deck_index=view.selected_deck_index,
            selected_deck=view.selected_deck,
            battle_command=view.battle_command,
            on_confirm=view.send_summary,
        )

        await switch_view.send_switch_prompt(interaction)


class SendInviteButton(Button):
    def __init__(self) -> None:
        super().__init__(label="Send Invitation", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction) -> None:
        view: BattleInviteView = self.view  # pyright: ignore[reportAssignmentType]

        for child in view.children:
            if isinstance(child, Button):
                child.disabled = True

        await interaction.response.edit_message(content="Battle started!", embed=None, view=view)

        if view.battle_command.opponent == "AI":
            new_view = await view.battle_command.run_ai()
        else:
            new_view = await view.battle_command.run_player()

        await new_view.update_ui(interaction)
        view.stop()
