from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands

from durin_tcg.commands.battling import BattleCommand

if TYPE_CHECKING:
    from durin_tcg.bot import DurinBot
    from durin_tcg.models.game_data import GameData


class Battling(commands.GroupCog, name="battle"):
    def __init__(self, bot: commands.Bot, game_data: GameData) -> None:
        self.bot = bot
        self.game_data = game_data

    @app_commands.command(name="profile", description="See your battle profile")
    async def battle_profile(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            content="This command hasn't been edited yet, but soon! Haha."
        )

    @app_commands.command(name="ai", description="Challenge an AI.")
    async def challenge_ai(self, interaction: discord.Interaction) -> None:
        await self._battle_command(interaction, "AI")

    @app_commands.command(name="player", description="Challenge another player")
    @app_commands.describe(opponent="The user you want to challenge.")
    async def challenge_player(
        self, interaction: discord.Interaction, opponent: discord.User
    ) -> None:
        if opponent.id == interaction.user.id:
            await interaction.response.send_message("You can't challenge yourself.", ephemeral=True)
            return

        await self._battle_command(interaction, opponent)

    async def _battle_command(
        self, interaction: discord.Interaction, opponent: discord.User | Literal["AI"]
    ) -> None:
        command = BattleCommand(
            challenger=interaction.user, opponent=opponent, game_data=self.game_data
        )

        await command.send_invite(interaction)


async def setup(bot: DurinBot) -> None:
    await bot.add_cog(Battling(bot, bot.game_data))
