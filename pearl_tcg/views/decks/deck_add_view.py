from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Interaction, SelectOption
from discord.ui import Modal, Select, TextInput, View

from pearl_tcg.constants import EMBED_TIMEOUT
from pearl_tcg.models.user import CardDeck, describe_deck
from pearl_tcg.views.base import BaseView

if TYPE_CHECKING:
    from pearl_tcg.models.game_data import GameData
    from pearl_tcg.models.owned_card import OwnedCard

# Discord's SelectOption cap per Select.
MAX_SELECT_OPTIONS = 25


def _build_options(available: list[OwnedCard]) -> list[SelectOption]:
    # Show the highest-rarity copies first when truncating to the cap.
    ranked = sorted(available, key=lambda c: c.rarity, reverse=True)[:MAX_SELECT_OPTIONS]
    return [
        SelectOption(
            label=owned.character_name,
            description=f"{owned.rarity}★ - {owned.condition.name.title()}",
            value=owned.id,
        )
        for owned in ranked
    ]


class DeckAddView(BaseView):
    def __init__(
        self,
        user_cards: list[OwnedCard],
        user_id: str,
        game_data: GameData,
        timeout: float = EMBED_TIMEOUT,
    ) -> None:
        super().__init__(timeout=timeout)
        self.user_cards = user_cards
        self.user_id = user_id
        self.game_data = game_data
        self.selected: list[str] = []  # OwnedCard.id values
        self.selected_character_names: set[str] = set()
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

    def describe_selected(self) -> str:
        by_id = {owned.id: owned for owned in self.user_cards}
        parts = []
        for instance_id in self.selected:
            owned = by_id.get(instance_id)
            parts.append(f"{owned.character_name} ({owned.rarity}★)" if owned else "(missing card)")
        return ", ".join(parts)

    async def finish_deck(self, interaction: Interaction) -> None:
        modal = DeckNameModal(self)
        await interaction.response.send_modal(modal)


class DeckCharacterSelect(Select):
    def __init__(self, index: int, parent: DeckAddView, enabled: bool = True) -> None:
        self.index = index
        self.parent = parent

        available = [
            c for c in parent.user_cards if c.character_name not in parent.selected_character_names
        ]

        super().__init__(
            placeholder=f"Select character {index + 1}",
            options=_build_options(available)
            or [SelectOption(label="No cards available", value="none")],
            min_values=1,
            max_values=1,
            disabled=not enabled,
        )

    async def callback(self, interaction: Interaction) -> None:
        chosen_id = self.values[0]
        chosen = next((c for c in self.parent.user_cards if c.id == chosen_id), None)

        if chosen is None or chosen.character_name in self.parent.selected_character_names:
            await interaction.response.send_message(
                "That character is no longer available to pick.", ephemeral=True
            )
            return

        self.parent.selected.append(chosen.id)
        self.parent.selected_character_names.add(chosen.character_name)
        self.disabled = True  # disable this dropdown

        # Enable the next select (if any)
        next_index = self.index + 1
        if next_index < len(self.parent.selects):
            next_select = self.parent.selects[next_index]
            next_select.disabled = False

            remaining = [
                c
                for c in self.parent.user_cards
                if c.character_name not in self.parent.selected_character_names
            ]
            next_select.options = _build_options(remaining) or [
                SelectOption(label="No cards available", value="none")
            ]

            await interaction.response.edit_message(
                content=f"Selected `{self.parent.describe_selected()}`. Choose the next character.",
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
            content=f"You selected: `{self.parent.describe_selected()}` and named it `{self.parent.deck_name}`.\nDo you want to save this as a deck?",
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

        deck = CardDeck(name=self.parent.deck_name, cards=self.parent.selected)
        user.decks.append(deck)
        self.parent.game_data.save_users()

        await interaction.response.edit_message(
            content=f"Deck `{self.parent.deck_name}` created with: `{describe_deck(user, deck)}`",
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
