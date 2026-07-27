from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ui import View

if TYPE_CHECKING:
    from durin_tcg.models.cards import Card


class CardAlbumPaginator(View):
    def __init__(
        self, user_cards: list[str], card_lookup: dict[str, Card], timeout: int = 60
    ) -> None:
        super().__init__(timeout=timeout)
        self.user_cards = list(user_cards)
        self.card_lookup = card_lookup
        self.index: int = 0

        self._update_buttons()

    def _get_embed(self) -> discord.Embed:
        current_card = self.card_lookup[self.user_cards[self.index]]

        embed = discord.Embed(
            title=current_card.name, description=f"Card {self.index + 1}/{len(self.user_cards)}"
        )

        embed.add_field(name="Basic Attack", value=current_card.basic.desc, inline=False)
        embed.add_field(name="Skill", value=current_card.skill.desc, inline=False)
        embed.add_field(name="Ultimate", value=current_card.ultimate.desc, inline=False)

        return embed

    def _update_buttons(self) -> None:
        self.first.disabled = self.index == 0
        self.prev.disabled = self.index == 0
        self.next.disabled = self.index == len(self.user_cards) - 1
        self.last.disabled = self.index == len(self.user_cards) - 1

    async def update_message(self, interaction: discord.Interaction) -> None:
        self._update_buttons()
        embed = self._get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⏪")
    async def first(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
        self.index = 0
        await self.update_message(interaction)

    @discord.ui.button(label="◀️")
    async def prev(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
        if self.index > 0:
            self.index -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="▶️")
    async def next(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
        if self.index < len(self.user_cards) - 1:
            self.index += 1
            await self.update_message(interaction)

    @discord.ui.button(label="⏩", style=discord.ButtonStyle.grey)
    async def last(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
        self.index = len(self.user_cards) - 1
        await self.update_message(interaction)
