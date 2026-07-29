from __future__ import annotations

import time
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from pearl_tcg.constants import (
    MANUAL_DROP_PER_GUILD_COOLDOWN_SECONDS,
    MANUAL_DROP_PER_USER_COOLDOWN_SECONDS,
)
from pearl_tcg.utils.drop_spawner import spawn_drop

if TYPE_CHECKING:
    from pearl_tcg.bot import PearlBot
    from pearl_tcg.models.game_data import GameData


class Drop(commands.GroupCog, name="drop"):
    channel = app_commands.Group(
        name="channel", description="Configure where cards drop in this server."
    )

    def __init__(self, bot: PearlBot, game_data: GameData) -> None:
        self.bot = bot
        self.game_data = game_data
        self._last_user_drop: dict[tuple[int, int], float] = {}
        self._last_guild_drop: dict[int, float] = {}

    @channel.command(name="set", description="Set the channel where cards drop.")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def channel_set(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        assert interaction.guild_id is not None  # enforced by guild_only()

        state = self.game_data.get_guild_drop_state(str(interaction.guild_id))
        state.drop_channel_id = channel.id
        self.game_data.save_guild_drop_states()

        await interaction.response.send_message(
            f"Cards will now drop in {channel.mention}.", ephemeral=True
        )

    @channel.command(name="show", description="Show the configured drop channel.")
    @app_commands.guild_only()
    async def channel_show(self, interaction: discord.Interaction) -> None:
        assert interaction.guild_id is not None  # enforced by guild_only()

        state = self.game_data.get_guild_drop_state(str(interaction.guild_id))
        if state.drop_channel_id is None:
            await interaction.response.send_message(
                "No drop channel configured yet.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Cards currently drop in <#{state.drop_channel_id}>.", ephemeral=True
        )

    @app_commands.command(name="now", description="Trigger a card drop right now.")
    @app_commands.guild_only()
    async def now(self, interaction: discord.Interaction) -> None:
        assert interaction.guild_id is not None  # enforced by guild_only()

        guild_id = interaction.guild_id
        user_key = (guild_id, interaction.user.id)
        now = time.monotonic()

        user_wait = MANUAL_DROP_PER_USER_COOLDOWN_SECONDS - (
            now - self._last_user_drop.get(user_key, 0.0)
        )
        if user_wait > 0:
            await interaction.response.send_message(
                f"Slow down! Try again in {user_wait:.1f}s.", ephemeral=True
            )
            return

        guild_wait = MANUAL_DROP_PER_GUILD_COOLDOWN_SECONDS - (
            now - self._last_guild_drop.get(guild_id, 0.0)
        )
        if guild_wait > 0:
            await interaction.response.send_message(
                f"A card just dropped in this server. Try again in {guild_wait:.1f}s.",
                ephemeral=True,
            )
            return

        state = self.game_data.get_guild_drop_state(str(guild_id))
        if state.drop_channel_id is None:
            await interaction.response.send_message(
                "No drop channel configured yet - ask an admin to run `/drop channel set`.",
                ephemeral=True,
            )
            return

        channel = self.bot.get_channel(state.drop_channel_id)
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "The configured drop channel no longer exists - ask an admin to set a new one.",
                ephemeral=True,
            )
            return

        self._last_user_drop[user_key] = now
        self._last_guild_drop[guild_id] = now

        await interaction.response.send_message("Dropping cards...", ephemeral=True)
        await spawn_drop(channel, self.game_data, str(guild_id))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None:
            return

        guild_id = str(message.guild.id)
        state = self.game_data.get_guild_drop_state(guild_id)
        if state.drop_channel_id != message.channel.id:
            return

        state.message_counter += 1
        if state.message_counter >= state.next_drop_threshold:
            await spawn_drop(message.channel, self.game_data, guild_id)


async def setup(bot: PearlBot) -> None:
    await bot.add_cog(Drop(bot, bot.game_data))
