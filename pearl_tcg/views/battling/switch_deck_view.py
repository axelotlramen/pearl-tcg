from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import discord
from discord import Embed, Interaction
from discord.ui import Button, Select

from durin_tcg.constants import EMBED_TIMEOUT
from durin_tcg.views.base import BaseView

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from durin_tcg.commands.battling import BattleCommand
    from durin_tcg.models.user import CardDeck


class SwitchDeckView(BaseView):
    def __init__(
        self,
        user: discord.User | discord.Member,
        selected_deck_index: int,
        selected_deck: CardDeck,
        battle_command: BattleCommand,
        on_confirm: Callable[[Interaction], Coroutine[Any, Any, None]],
        timeout: float = EMBED_TIMEOUT,
    ) -> None:
        super().__init__(timeout=timeout)

        self.user = user
        self.battle_command = battle_command
        self.on_confirm = on_confirm

        self.selected_deck_index: int = selected_deck_index
        self.selected_deck = selected_deck
        self.all_decks = self._get_user_all_decks()

        self.message: discord.Message | None = None

        self.add_item(DeckSelect(self.all_decks))
        self.add_item(ConfirmSwitchDeckButton())

    def _get_user_all_decks(self) -> list[CardDeck]:
        return self.battle_command.game_data.get_user(str(self.user.id)).decks

    async def send_switch_prompt(self, interaction: Interaction) -> None:
        embed = Embed(
            title="Switch Your Deck",
            description=f"Select a different deck to use for this battle.\nYour current deck is `{self.selected_deck.name}` with `{', '.join(self.selected_deck.cards)}`",
            color=discord.Color.orange(),
        )
        await interaction.response.edit_message(embed=embed, view=self)

        self.message = await interaction.original_response()


class DeckSelect(Select):
    def __init__(self, all_decks: list[CardDeck]) -> None:
        options = [
            discord.SelectOption(
                label=deck.name, description=", ".join(deck.cards), value=str(deck_num)
            )
            for deck_num, deck in enumerate(all_decks)
        ]
        super().__init__(placeholder="Choose a deck", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        view: SwitchDeckView = self.view  # pyright: ignore[reportAssignmentType]

        view.selected_deck_index = int(self.values[0])
        selected_deck_name = view.all_decks[view.selected_deck_index].name
        selected_deck_cards = ", ".join(view.all_decks[view.selected_deck_index].cards)

        await interaction.response.edit_message(
            content=f"Deck `{selected_deck_name}` with `{selected_deck_cards}` selected. Click **Confirm Switch** to continue.",
            view=view,
            embed=None,
        )


class ConfirmSwitchDeckButton(Button):
    def __init__(self) -> None:
        super().__init__(label="Confirm Switch", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction) -> None:
        view: SwitchDeckView = self.view  # pyright: ignore[reportAssignmentType]

        view.battle_command.switch_deck(view.user, view.selected_deck_index)

        with contextlib.suppress(discord.NotFound):
            await interaction.message.edit(  # pyright: ignore[reportOptionalMemberAccess]
                content="Deck switched successfully!", view=None, embed=None
            )

        with contextlib.suppress(discord.InteractionResponded):
            await interaction.response.defer(ephemeral=True)

        await view.on_confirm(interaction)
