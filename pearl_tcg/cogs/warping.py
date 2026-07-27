from __future__ import annotations

import random
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from durin_tcg.bot import DurinBot

if TYPE_CHECKING:
    from durin_tcg.bot import DurinBot
    from durin_tcg.models.game_data import GameData


class Warping(commands.GroupCog, name="warp"):
    def __init__(self, bot: commands.Bot, game_data: GameData) -> None:
        self.bot = bot
        self.game_data = game_data

    @app_commands.command(
        name="single", description="Warp once for a chance to receive currency or a card."
    )
    async def warp_single(self, interaction: discord.Interaction) -> None:
        await self._handle_warp(interaction, pulls=1)

    @app_commands.command(
        name="ten", description="Warp ten times for a chance to receive cards or currency."
    )
    async def warp_ten(self, interaction: discord.Interaction) -> None:
        await self._handle_warp(interaction, pulls=10)

    async def _handle_warp(self, interaction: discord.Interaction, pulls: int) -> None:
        await interaction.response.defer()
        users = self.game_data.users
        uid = str(interaction.user.id)

        results = []
        for _ in range(pulls):
            result_type = random.choices(["currency", "card"], weights=[80, 20])[0]

            if result_type == "currency":
                amount = random.randint(10, 50)
                self.game_data.add_currency(uid, amount)
                results.append(f"💰 +{amount} currency")
            else:
                card_names = list(self.game_data.cards.keys())
                card = random.choice(card_names)
                already_owned = card in users[uid].owned_cards
                self.game_data.add_card(uid, card)
                results.append(
                    f"✨ New card: **{card}**"
                    if not already_owned
                    else f"📦 Duplicate card: **{card}**"
                )

        self.game_data.save_users()

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Warp Results",
            description="\n".join(results),
            color=discord.Color.gold(),
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: DurinBot) -> None:
    await bot.add_cog(Warping(bot, bot.game_data))
