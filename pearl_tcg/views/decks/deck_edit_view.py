from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Interaction, SelectOption
from discord.ui import Button, Modal, Select, TextInput, View

from pearl_tcg.constants import EMBED_TIMEOUT
from pearl_tcg.models.user import describe_deck
from pearl_tcg.views.base import BaseView

if TYPE_CHECKING:
    from pearl_tcg.models.game_data import GameData
    from pearl_tcg.models.owned_card import OwnedCard
    from pearl_tcg.models.user import CardDeck

MAX_SELECT_OPTIONS = 25


def _build_options(cards: list[OwnedCard], selected_id: str | None) -> list[SelectOption]:
    ranked = sorted(cards, key=lambda c: c.rarity, reverse=True)
    if selected_id is not None and not any(
        c.id == selected_id for c in ranked[:MAX_SELECT_OPTIONS]
    ):
        selected_card = next((c for c in ranked if c.id == selected_id), None)
        if selected_card is not None:
            ranked = [selected_card, *[c for c in ranked if c.id != selected_id]]

    limited = ranked[:MAX_SELECT_OPTIONS]
    if not limited:
        return [SelectOption(label="No cards available", value="none")]

    return [
        SelectOption(
            label=owned.character_name,
            description=f"{owned.rarity}★ - {owned.condition.name.title()}",
            value=owned.id,
            default=(owned.id == selected_id),
        )
        for owned in limited
    ]


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
        self.selected: list[str] = list(self.deck.cards)

        self.character_selects: list[EditableCharacterSelect] = []

        for i in range(4):
            select = EditableCharacterSelect(
                index=i,
                parent_view=self,
                selected_instance_id=self.selected[i] if i < len(self.selected) else None,
            )
            self.character_selects.append(select)
            self.add_item(select)

        self.add_item(ChangeDeckNameButton(parent_view=self))
        self.add_item(SaveChangesButton(parent_view=self))
        self.add_item(ResetChangesButton(parent_view=self))

    def edit_selected_deck(self, new_instance_id: str, index: int) -> None:
        while len(self.selected) <= index:
            self.selected.append("")
        self.selected[index] = new_instance_id

    def character_name_for(self, instance_id: str) -> str | None:
        owned = self.game_data.get_owned_card(self.user_id, instance_id)
        return owned.character_name if owned else None


class EditableCharacterSelect(Select):
    def __init__(
        self, index: int, parent_view: SingleEditDeckView, selected_instance_id: str | None
    ) -> None:
        self.index = index
        self.parent_view = parent_view

        user_cards = parent_view.user.owned_cards
        default_id = selected_instance_id or (user_cards[0].id if user_cards else None)

        super().__init__(
            placeholder=f"Character {index + 1}",
            options=_build_options(user_cards, default_id),
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: Interaction) -> None:
        self.parent_view.edit_selected_deck(self.values[0], self.index)
        await interaction.response.defer()


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

        selected_ids = self.parent_view.selected
        character_names = [self.parent_view.character_name_for(iid) for iid in selected_ids]

        if any(name is None for name in character_names):
            await interaction.response.send_message(
                "One of the selected cards is no longer in your collection.", ephemeral=True
            )
            return
        if len(set(character_names)) < len(character_names):
            await interaction.response.send_message(
                "A deck cannot contain duplicate characters.", ephemeral=True
            )
            return

        self.parent_view.deck.cards = selected_ids
        self.parent_view.deck.name = self.parent_view.deck_name
        self.parent_view.game_data.save_users()

        for select in self.parent_view.character_selects:
            select.disabled = True

        for item in list(self.parent_view.children):
            if isinstance(item, Button):
                self.parent_view.remove_item(item)

        description = describe_deck(self.parent_view.user, self.parent_view.deck)
        await interaction.response.edit_message(
            content=f"Deck successfully updated to **{self.parent_view.deck.name}**: `{description}`",
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
        self.parent_view.selected = list(self.parent_view.deck.cards)
        self.parent_view.character_selects.clear()
        for i in range(4):
            select = EditableCharacterSelect(
                index=i,
                parent_view=self.parent_view,
                selected_instance_id=(
                    self.parent_view.deck.cards[i] if i < len(self.parent_view.deck.cards) else None
                ),
            )
            self.parent_view.character_selects.append(select)
            self.parent_view.add_item(select)

        description = describe_deck(self.parent_view.user, self.parent_view.deck)
        await interaction.response.edit_message(
            content=f"Changes reset to original deck **{self.parent_view.deck.name}**: `{description}`",
            view=self.parent_view,
        )
