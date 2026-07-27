"""
Copied and Edited from Python-Discord-Bot-Template: https://github.com/kkrypt0nn/Python-Discord-Bot-Template/blob/main/bot.py
"""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext import commands, tasks

from durin_tcg.models.game_data import GameData

from .utils.logger import LOGGER

if TYPE_CHECKING:
    from discord.ext.commands import Context


class DurinBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="a!", intents=discord.Intents.all(), help_command=None)

        self.initialised = False
        self.logger = LOGGER
        self.game_data = GameData()

    async def _load_cogs(self) -> None:
        for filepath in Path("durin_tcg/cogs").glob("**/*.py"):
            extension = Path(filepath).stem

            try:
                await self.load_extension(f"durin_tcg.cogs.{extension}")
                self.logger.info("Loaded extension '%s'", extension)
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                self.logger.exception("Failed to load extension '%s'\n'%s'", extension, exception)

    @tasks.loop(minutes=5.0)
    async def status_task(self) -> None:
        try:
            song = "「アイドル」by YOASOBI"
            await self.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening, name=song)
            )
        except Exception:
            self.logger.exception("Status task failed.")

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        if self.user:
            self.logger.info("Logged in as %s", self.user.name)
        self.logger.info("discord API version: %s", discord.__version__)
        self.logger.info("Python version: %s", platform.python_version())
        self.logger.info("Running on %s %s (%s)", platform.system(), platform.release(), os.name)
        self.logger.info("-------------------")

        await self._load_cogs()
        self.status_task.start()

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_command(self, ctx: Context) -> None:
        executed_command = ctx.command.qualified_name if ctx.command else "Unknown"
        if ctx.guild is not None:
            self.logger.info(
                "Executed %s command in %s (ID: %s) by %s (ID: %s)",
                executed_command,
                ctx.guild.name,
                ctx.guild.id,
                ctx.author,
                ctx.author.id,
            )
        else:
            self.logger.info(
                "Executed %s command by %s (ID: %s) in DMs",
                executed_command,
                ctx.author,
                ctx.author.id,
            )

    async def on_command_error(self, _context: Context, error: Exception) -> None:
        raise error
