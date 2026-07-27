from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from durin_tcg.enums import Game
from durin_tcg.models.cards import Card
from durin_tcg.views.card_album_view import CardAlbumPaginator

if TYPE_CHECKING:
    from durin_tcg.bot import DurinBot
    from durin_tcg.models.game_data import GameData


class CardGame(commands.GroupCog, name="cards"):
    def __init__(self, bot: commands.Bot, game_data: GameData) -> None:
        self.bot = bot
        self.game_data = game_data

    @app_commands.command(name="my", description="List all cards in a user's collection.")
    async def list_user_cards(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        uid = str(interaction.user.id)

        if uid not in self.game_data.users:
            self.game_data.add_user(uid)
            await interaction.followup.send(
                "You don't own any cards yet, but your Durin TCG account has been created. Please use `/warp` to get some cards."
            )
            return

        user = self.game_data.get_user(uid)

        if not user.owned_cards:
            await interaction.followup.send(
                "You don't own any cards yet. Please use `/warp` or wait for `@axelotlramen` to implement this feature."
            )
            return

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Card Collection", color=discord.Color.green()
        )

        for card in user.owned_cards:
            embed.add_field(name=card, value="", inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="all", description="List all available cards.")
    async def list_all_cards(self, interaction: discord.Interaction) -> None:
        cards = self.game_data.cards
        if not cards:
            await interaction.response.send_message("No cards found.", ephemeral=True)
            return

        cards_by_game: dict[Game, list[Card]] = defaultdict(list)
        for card in cards.values():
            cards_by_game[card.game].append(card)

        embed = discord.Embed(
            title="All Available Cards",
            description="Here's a list of all cards and their elements:",
            color=discord.Color.blurple(),
        )

        for game in sorted(cards_by_game.keys()):
            card_lines = [
                f"• **{card.name}** — {card.element.value}"
                for card in sorted(cards_by_game[game], key=lambda c: c.name)
            ]
            embed.add_field(name=f"{game.value} Cards", value="\n".join(card_lines), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="album", description="List cards in an album format.")
    async def list_all_cards_album(self, interaction: discord.Interaction) -> None:
        cards = self.game_data.cards
        if not cards:
            await interaction.response.send_message("No cards found.")
            return

        user = self.game_data.get_user(str(interaction.user.id))

        if not user or not user.owned_cards:
            await interaction.response.send_message(
                "You don't own any cards yet. Please use `/warp` or wait for `@axelotlramen` to implement this feature."
            )
            return

        view = CardAlbumPaginator(user.owned_cards, cards)
        await interaction.response.send_message(embed=view._get_embed(), view=view)


async def setup(bot: DurinBot) -> None:
    await bot.add_cog(CardGame(bot, bot.game_data))
