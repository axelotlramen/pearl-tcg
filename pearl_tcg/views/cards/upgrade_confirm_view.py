from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Interaction

from pearl_tcg.constants import CONDITION_UPGRADE_COST, EMBED_TIMEOUT
from pearl_tcg.enums import CardCondition
from pearl_tcg.views.base import BaseView

if TYPE_CHECKING:
    from pearl_tcg.models.game_data import GameData


class UpgradeConfirmView(BaseView):
    def __init__(
        self,
        user_id: str,
        instance_id: str,
        game_data: GameData,
        timeout: float = EMBED_TIMEOUT,
    ) -> None:
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.instance_id = instance_id
        self.game_data = game_data

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: Interaction, _button: discord.ui.Button) -> None:
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "This isn't your upgrade to confirm.", ephemeral=True
            )
            return

        user = self.game_data.get_user(self.user_id)
        owned = self.game_data.get_owned_card(self.user_id, self.instance_id)

        if owned is None or owned.condition == CardCondition.MINT:
            await interaction.response.edit_message(
                content="That card can no longer be upgraded.", view=None
            )
            self.stop()
            return

        cost = CONDITION_UPGRADE_COST[owned.condition]
        if user.materials < cost:
            await interaction.response.edit_message(
                content="You no longer have enough materials.", view=None
            )
            self.stop()
            return

        user.materials -= cost
        owned.condition = CardCondition(owned.condition + 1)
        self.game_data.save_users()

        await interaction.response.edit_message(
            content=f"**{owned.character_name}** is now {owned.condition.name.title()}!",
            view=None,
        )
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: Interaction, _button: discord.ui.Button) -> None:
        await interaction.response.edit_message(content="Upgrade canceled.", view=None)
        self.stop()
