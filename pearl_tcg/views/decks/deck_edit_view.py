from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Interaction, SelectOption
from discord.ui import Button, Modal, Select, TextInput, View

from durin_tcg.constants import EMBED_TIMEOUT
from durin_tcg.models.game_data import GameData
from durin_tcg.views.base import BaseView

if TYPE_CHECKING:
    from durin_tcg.models.game_data import GameData
    from durin_tcg.models.user import CardDeck


class EditDeckView(BaseView):
    def __init__(
        self,
        user_id: str,
        game_data: GameData,
        decks: list[CardDeck],
        timeout: float = EMBED_TIMEOUT,
    ) -> None:
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.game_data = game_data
        self.decks = decks

        self.add_item(EditDeckSelect(self))


class EditDeckSelect(Select):
    def __init__(self, parent_view: EditDeckView) -> None:
        self.parent_view = parent_view

        options = [
            SelectOption(label=f"{deck.name or f'Deck {i + 1}'}", value=str(i))
            for i, deck in enumerate(self.parent_view.decks)
        ]

        super().__init__(
            placeholder="Choose a deck to edit", options=options, min_values=1, max_values=1
        )

    async def callback(self, interaction: Interaction) -> None:
        index = int(self.values[0])
        view = SingleEditDeckView(
            deck_index=index, user_id=self.parent_view.user_id, game_data=self.parent_view.game_data
        )

        await interaction.response.edit_message(
            content=f"Editing Deck {index + 1}: **{self.parent_view.decks[index].name}**", view=view
        )


class SingleEditDeckView(View):
    def __init__(self, deck_index: int, user_id: str, game_data: GameData) -> None:
        super().__init__(timeout=120)
        self.deck_index = deck_index
        self.user_id = user_id
        self.game_data = game_data

        self.user = game_data.get_user(user_id)
        self.deck = self.user.decks[deck_index]

        self.deck_name = self.deck.name
        self.selected = self.deck.cards

        self.character_selects: list[EditableCharacterSelect] = []

        for i in range(4):
            select = EditableCharacterSelect(
                index=i,
                parent_view=self,
                selected_char=self.deck.cards[i] if i < len(self.deck.cards) else None,
            )
            self.character_selects.append(select)
            self.add_item(select)

        self.add_item(ChangeDeckNameButton(parent_view=self))
        self.add_item(SaveChangesButton(parent_view=self))
        self.add_item(ResetChangesButton(parent_view=self))

    def edit_selected_deck(self, new_character: str, index: int) -> None:
        self.selected[index] = new_character


class EditableCharacterSelect(Select):
    def __init__(
        self, index: int, parent_view: SingleEditDeckView, selected_char: str | None
    ) -> None:
        self.index = index
        self.parent_view = parent_view

        user_cards = parent_view.user.owned_cards
        selected = selected_char or (user_cards[0] if user_cards else "")

        options = [
            SelectOption(label=name, value=name, default=(name == selected)) for name in user_cards
        ]

        super().__init__(
            placeholder=f"Character {index + 1}", options=options, min_values=1, max_values=1
        )

    async def callback(self, interaction: Interaction) -> None:
        self.parent_view.edit_selected_deck(self.values[0], self.index)
        await interaction.response.defer()
        # You could auto-update here if you want


class ChangeDeckNameButton(Button):
    def __init__(self, parent_view: SingleEditDeckView) -> None:
        super().__init__(label="Change Name", style=discord.ButtonStyle.secondary)
        self.parent_view = parent_view

    async def callback(self, interaction: Interaction) -> None:
        if interaction.user.id != int(self.parent_view.user_id):
            await interaction.response.send_message(
                "You can't rename someone else's deck.", ephemeral=True
            )
            return

        await interaction.response.send_modal(ChangeDeckNameModal(self.parent_view))


class ChangeDeckNameModal(Modal, title="Rename Your Deck"):
    def __init__(self, parent_view: SingleEditDeckView) -> None:
        super().__init__(timeout=60)
        self.parent_view = parent_view

        self.name_input = TextInput(
            label="New Deck Name", placeholder="Enter a new name", max_length=30
        )
        self.add_item(self.name_input)

    async def on_submit(self, interaction: Interaction) -> None:
        self.parent_view.deck_name = self.name_input.value

        await interaction.response.edit_message(
            content=f"NOT SAVED: Deck name is **{self.parent_view.deck_name}**"
        )


class SaveChangesButton(Button):
    def __init__(self, parent_view: SingleEditDeckView) -> None:
        super().__init__(label="Save Changes", style=discord.ButtonStyle.success)
        self.parent_view = parent_view

    async def callback(self, interaction: Interaction) -> None:
        if interaction.user.id != int(self.parent_view.user_id):
            await interaction.response.send_message(
                "You can't save changes for someone else's deck.", ephemeral=True
            )
            return

        selected_chars = self.parent_view.selected

        if len(set(selected_chars)) < len(selected_chars):
            await interaction.response.send_message(
                "A deck cannot contain duplicate characters.", ephemeral=True
            )
            return

        self.parent_view.deck.cards = selected_chars
        self.parent_view.deck.name = self.parent_view.deck_name
        self.parent_view.game_data.save_users()

        for select in self.parent_view.character_selects:
            select.disabled = True

        for item in list(self.parent_view.children):
            if isinstance(item, Button):
                self.parent_view.remove_item(item)

        await interaction.response.edit_message(
            content=f"Deck successfully updated to **{self.parent_view.deck.name}**: `{', '.join(selected_chars)}`",
            view=self.parent_view,
        )
        self.parent_view.stop()


class ResetChangesButton(Button):
    def __init__(self, parent_view: SingleEditDeckView) -> None:
        super().__init__(label="Reset Changes", style=discord.ButtonStyle.danger)
        self.parent_view = parent_view

    async def callback(self, interaction: Interaction) -> None:
        if interaction.user.id != int(self.parent_view.user_id):
            await interaction.response.send_message(
                "You can't reset someone else's deck.", ephemeral=True
            )
            return

        # Remove old selects
        for select in self.parent_view.character_selects:
            self.parent_view.remove_item(select)

        # Recreate selects from original deck
        self.parent_view.character_selects.clear()
        for i in range(4):
            select = EditableCharacterSelect(
                index=i, parent_view=self.parent_view, selected_char=self.parent_view.deck.cards[i]
            )
            self.parent_view.character_selects.append(select)
            self.parent_view.add_item(select)

        await interaction.response.edit_message(
            content=f"Changes reset to original deck **{self.parent_view.deck.name}**: `{', '.join(self.parent_view.deck.cards)}`",
            view=self.parent_view,
        )
