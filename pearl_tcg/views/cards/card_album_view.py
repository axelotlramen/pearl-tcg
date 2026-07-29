from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from pearl_tcg.models.owned_card import compute_combat_atk
from pearl_tcg.views.base import BaseView
from pearl_tcg.views.card_action_view import CardActionView

if TYPE_CHECKING:
    from pearl_tcg.models.cards import Card
    from pearl_tcg.models.game_data import GameData
    from pearl_tcg.models.owned_card import OwnedCard


class CardAlbumPaginator(BaseView):
    def __init__(
        self,
        owned_cards: list[OwnedCard],
        card_lookup: dict[str, Card],
        user_id: str,
        game_data: GameData,
        timeout: float = 60,
    ) -> None:
        super().__init__(timeout=timeout)
        self.owned_cards = list(owned_cards)
        self.card_lookup = card_lookup
        self.user_id = user_id
        self.game_data = game_data
        self.index: int = 0

        self._update_buttons()

    def get_embed(self) -> discord.Embed:
        instance = self.owned_cards[self.index]
        card = self.card_lookup.get(instance.character_name)

        embed = discord.Embed(
            title=instance.character_name,
            description=(
                f"Card {self.index + 1}/{len(self.owned_cards)}\n"
                f"{instance.rarity}★ - {instance.condition.name.title()} condition - "
                f"{instance.border} border"
            ),
        )

        if card is None:
            embed.add_field(
                name="Unavailable",
                value="This card's character no longer exists in the current roster.",
                inline=False,
            )
        else:
            embed.description = f"{embed.description}\n{card.path.value} - {card.element.value}"
            embed.add_field(
                name="Combat ATK", value=str(compute_combat_atk(card, instance)), inline=False
            )
            embed.add_field(name="Basic Attack", value=card.basic.desc, inline=False)
            embed.add_field(name="Skill", value=card.skill.desc, inline=False)
            embed.add_field(name="Ultimate", value=card.ultimate.desc, inline=False)

        return embed

    def _update_buttons(self) -> None:
        self.first.disabled = self.index == 0
        self.prev.disabled = self.index == 0
        self.next.disabled = self.index == len(self.owned_cards) - 1
        self.last.disabled = self.index == len(self.owned_cards) - 1

    async def update_message(self, interaction: discord.Interaction) -> None:
        self._update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

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
        if self.index < len(self.owned_cards) - 1:
            self.index += 1
            await self.update_message(interaction)

    @discord.ui.button(label="⏩", style=discord.ButtonStyle.grey)
    async def last(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
        self.index = len(self.owned_cards) - 1
        await self.update_message(interaction)

    @discord.ui.button(label="Manage", style=discord.ButtonStyle.blurple, row=1)
    async def manage(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("This isn't your card.", ephemeral=True)
            return

        instance = self.owned_cards[self.index]
        await interaction.response.send_message(
            f"Manage **{instance.character_name}** ({instance.rarity}★):",
            view=CardActionView(instance.id, self.user_id, self.game_data),
            ephemeral=True,
        )
