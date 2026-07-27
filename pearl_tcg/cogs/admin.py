from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from durin_tcg.bot import DurinBot
from durin_tcg.l10n import LocaleStr

if TYPE_CHECKING:
    from durin_tcg.bot import DurinBot

LOCALE_NAME_MAP = {loc.value: loc for loc in discord.Locale}


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def sync(self, context: Context) -> None:
        context.bot.tree.copy_global_to(guild=context.guild)
        synced_commands = await self.bot.tree.sync(guild=context.guild)
        embed = discord.Embed(
            description=f"{len(synced_commands)} slash commands have been synchronized in this guild.",
            color=0xBEBEFE,
        )
        await context.send(embed=embed)

    @app_commands.command(
        name="test_locale", description="Test a translation with a different locale."
    )
    async def test_locale(self, interaction: Interaction, locale_code: str) -> None:
        locale_obj = LOCALE_NAME_MAP.get(locale_code)
        if not locale_obj:
            await interaction.response.send_message(f"Unknown locale code: `{locale_code}`")
            return

        test_message = LocaleStr("info.ping", latency=self.bot.latency).translate(locale_obj)

        await interaction.response.send_message(
            f"**Locale:** `{locale_code}`\n**Translation:** {test_message}"
        )


async def setup(bot: DurinBot) -> None:
    bot.remove_command("help")
    await bot.add_cog(Admin(bot))
