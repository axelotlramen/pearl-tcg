from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Interaction, SelectOption
from discord.ui import Modal, Select, TextInput, View

from durin_tcg.constants import EMBED_TIMEOUT
from durin_tcg.models.user import CardDeck
from durin_tcg.views.base import BaseView

if TYPE_CHECKING:
    from durin_tcg.models.game_data import GameData


class DeckAddView(BaseView):
    def __init__(
        self,
        user_cards: list[str],
        user_id: str,
        game_data: GameData,
        timeout: float = EMBED_TIMEOUT,
    ) -> None:
        super().__init__(timeout=timeout)
        self.user_cards = user_cards
        self.user_id = user_id
        self.game_data = game_data
        self.selected: list[str] = []
        self.deck_name: str = ""

        self.selects: list[DeckCharacterSelect] = []

        for i in range(4):
            select = DeckCharacterSelect(
                index=i,
                parent=self,
                enabled=(i == 0),  # Only the first one is enabled initially
            )
            self.selects.append(select)
            self.add_item(select)

    async def finish_deck(self, interaction: Interaction) -> None:
        modal = DeckNameModal(self)
        await interaction.response.send_modal(modal)


class DeckCharacterSelect(Select):
    def __init__(self, index: int, parent: DeckAddView, enabled: bool = True) -> None:
        self.index = index
        self.parent = parent

        available = [c for c in self.parent.user_cards if c not in self.parent.selected]

        options = [SelectOption(label=name, value=name) for name in available]

        super().__init__(
            placeholder=f"Select character {index + 1}",
            options=options,
            min_values=1,
            max_values=1,
            disabled=not enabled,
        )

    async def callback(self, interaction: Interaction) -> None:
        chosen = self.values[0]

        if chosen in self.parent.selected:
            await interaction.response.send_message(
                "You already selected that character!", ephemeral=True
            )
            return

        self.parent.selected.append(chosen)
        self.disabled = True  # disable this dropdown

        # Enable the next select (if any)
        next_index = self.index + 1
        if next_index < len(self.parent.selects):
            self.parent.selects[next_index].disabled = False

            # Update next select's options to exclude already picked
            remaining = [c for c in self.parent.user_cards if c not in self.parent.selected]
            self.parent.selects[next_index].options = [
                SelectOption(label=c, value=c) for c in remaining
            ]

            await interaction.response.edit_message(
                content=f"Selected `{', '.join(self.parent.selected)}`. Choose the next character.",
                view=self.parent,
            )
        else:
            await self.parent.finish_deck(interaction)


class DeckNameModal(Modal, title="Name Your Deck"):
    def __init__(self, parent: DeckAddView) -> None:
        super().__init__(timeout=60)
        self.parent = parent

        self.deck_name_input = TextInput(
            label="Deck Name", placeholder="Enter a name for your deck", max_length=30
        )

        self.add_item(self.deck_name_input)

    async def on_submit(self, interaction: Interaction) -> None:
        self.parent.deck_name = self.deck_name_input.value

        confirm_view = ConfirmCancelView(self.parent, interaction.user)
        await interaction.response.edit_message(
            content=f"You selected: `{', '.join(self.parent.selected)}` and named it `{self.parent.deck_name}`.\nDo you want to save this as a deck?",
            view=confirm_view,
        )


class ConfirmCancelView(View):
    def __init__(self, parent_view: DeckAddView, user: discord.User | discord.Member) -> None:
        super().__init__(timeout=60)
        self.parent = parent_view
        self.user = user

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: Interaction, _button: discord.ui.Button) -> None:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You can't confirm someone else's deck!", ephemeral=True
            )
            return

        user = self.parent.game_data.get_user(self.parent.user_id)

        if len(user.decks) >= 10:
            await interaction.response.edit_message(
                content="You reached the maximum number of decks (10).", view=None
            )
            self.parent.stop()
            return

        user.decks.append(CardDeck(name=self.parent.deck_name, cards=self.parent.selected))
        self.parent.game_data.save_users()

        await interaction.response.edit_message(
            content=f"Deck `{self.parent.deck_name}`created with: `{', '.join(self.parent.selected)}`",
            view=None,
        )
        self.parent.stop()
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: Interaction, _button: discord.ui.Button) -> None:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You can't cancel someone else's deck!", ephemeral=True
            )
            return

        await interaction.response.edit_message(content="Deck creation canceled.", view=None)
        self.parent.stop()
        self.stop()
