from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import discord

from pearl_tcg.constants import DROP_CLAIM_TIMEOUT_SECONDS
from pearl_tcg.views.base import BaseView
from pearl_tcg.views.card_action_view import CardActionView

if TYPE_CHECKING:
    from pearl_tcg.enums import CardRarity
    from pearl_tcg.models.game_data import GameData


@dataclass
class DropSlot:
    character_name: str
    rarity: CardRarity
    claimed_by: str | None = None


def build_drop_embed(slots: list[DropSlot]) -> discord.Embed:
    embed = discord.Embed(
        title="Cards have appeared!",
        description="Click a button below to claim that card - first come, first served.",
        color=discord.Color.gold(),
    )
    for index, slot in enumerate(slots, start=1):
        embed.add_field(
            name=f"Card {index}",
            value=f"{slot.character_name} {'★' * slot.rarity}",
            inline=True,
        )
    return embed


class DropClaimView(BaseView):
    def __init__(self, slots: list[DropSlot], game_data: GameData, guild_id: str) -> None:
        super().__init__(timeout=DROP_CLAIM_TIMEOUT_SECONDS)
        self.slots = slots
        self.game_data = game_data
        self.guild_id = guild_id
        self.claimed_user_ids: set[str] = set()

        for index in range(len(slots)):
            self.add_item(DropClaimButton(index=index, parent_view=self))


class DropClaimButton(discord.ui.Button):
    def __init__(self, index: int, parent_view: DropClaimView) -> None:
        slot = parent_view.slots[index]
        super().__init__(
            label=f"{slot.character_name} {'★' * slot.rarity}",
            style=discord.ButtonStyle.primary,
        )
        self.index = index
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction) -> None:
        slot = self.parent_view.slots[self.index]
        uid = str(interaction.user.id)

        if slot.claimed_by is not None:
            await interaction.response.send_message(
                "Someone already claimed that card.", ephemeral=True
            )
            return
        if uid in self.parent_view.claimed_user_ids:
            await interaction.response.send_message(
                "You already claimed a card from this drop.", ephemeral=True
            )
            return

        slot.claimed_by = uid
        self.parent_view.claimed_user_ids.add(uid)
        self.disabled = True
        self.label = f"{slot.character_name} - claimed"
        self.style = discord.ButtonStyle.secondary

        game_data = self.parent_view.game_data
        instance = game_data.add_owned_card(uid, slot.character_name, slot.rarity)
        game_data.save_users()

        await interaction.response.edit_message(view=self.parent_view)
        await interaction.followup.send(
            f"You claimed a {slot.rarity}★ **{slot.character_name}**!",
            ephemeral=True,
            view=CardActionView(instance.id, uid, game_data),
        )
