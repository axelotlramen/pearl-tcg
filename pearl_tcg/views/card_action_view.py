from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Interaction

from pearl_tcg.constants import DISCARD_MATERIALS_BY_RARITY, EMBED_TIMEOUT, SELL_VALUE_BY_RARITY
from pearl_tcg.views.base import BaseView

if TYPE_CHECKING:
    from pearl_tcg.models.game_data import GameData


class CardActionView(BaseView):
    """Sell, discard, or keep one owned card instance."""

    def __init__(
        self,
        instance_id: str,
        user_id: str,
        game_data: GameData,
        timeout: float = EMBED_TIMEOUT,
    ) -> None:
        super().__init__(timeout=timeout)
        self.instance_id = instance_id
        self.user_id = user_id
        self.game_data = game_data

    async def _authorized(self, interaction: Interaction) -> bool:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("This isn't your card.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Sell", style=discord.ButtonStyle.success)
    async def sell(self, interaction: Interaction, _button: discord.ui.Button) -> None:
        if not await self._authorized(interaction):
            return

        instance = self.game_data.remove_owned_card(self.user_id, self.instance_id)
        if instance is None:
            await interaction.response.edit_message(
                content="That card is no longer in your collection.", view=None
            )
            self.stop()
            return

        value = SELL_VALUE_BY_RARITY[instance.rarity]
        self.game_data.add_currency(self.user_id, value)
        self.game_data.save_users()

        await interaction.response.edit_message(
            content=f"Sold **{instance.character_name}** ({instance.rarity}★) for {value} currency.",
            view=None,
        )
        self.stop()

    @discord.ui.button(label="Discard", style=discord.ButtonStyle.danger)
    async def discard(self, interaction: Interaction, _button: discord.ui.Button) -> None:
        if not await self._authorized(interaction):
            return

        instance = self.game_data.remove_owned_card(self.user_id, self.instance_id)
        if instance is None:
            await interaction.response.edit_message(
                content="That card is no longer in your collection.", view=None
            )
            self.stop()
            return

        materials = DISCARD_MATERIALS_BY_RARITY[instance.rarity]
        self.game_data.get_user(self.user_id).materials += materials
        self.game_data.save_users()

        await interaction.response.edit_message(
            content=f"Discarded **{instance.character_name}** ({instance.rarity}★) for {materials} materials.",
            view=None,
        )
        self.stop()

    @discord.ui.button(label="Keep", style=discord.ButtonStyle.secondary)
    async def keep(self, interaction: Interaction, _button: discord.ui.Button) -> None:
        if not await self._authorized(interaction):
            return

        await interaction.response.edit_message(content="Kept in your collection.", view=None)
        self.stop()
