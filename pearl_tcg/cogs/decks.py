from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from pearl_tcg.constants import NEW_ACCOUNT_MESSAGE
from pearl_tcg.models.user import describe_deck
from pearl_tcg.views.decks.deck_add_view import DeckAddView
from pearl_tcg.views.decks.deck_delete_view import DeleteDeckView
from pearl_tcg.views.decks.deck_edit_view import EditDeckView

if TYPE_CHECKING:
    from pearl_tcg.bot import PearlBot
    from pearl_tcg.models.game_data import GameData


class Decks(commands.GroupCog, name="decks"):
    def __init__(self, bot: PearlBot, game_data: GameData) -> None:
        self.bot = bot
        self.game_data = game_data

    @app_commands.command(name="view", description="List all decks in a user's collection.")
    async def list_user_decks(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        uid = str(interaction.user.id)
        user, is_new = self.game_data.get_or_create_user(uid)

        if is_new:
            await interaction.followup.send(NEW_ACCOUNT_MESSAGE)
            return

        if not user.decks:
            await interaction.followup.send(
                "You haven't configured any decks yet. Please use `/decks add` or wait for `@axelotlramen` to implement this feature."
            )
            return

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Decks", color=discord.Color.green()
        )

        for deck_num, deck in enumerate(user.decks):
            embed.add_field(
                name=f"Deck {deck_num + 1}: {deck.name}",
                value=f"`{describe_deck(user, deck)}`",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="add", description="List all available cards.")
    async def add_deck(self, interaction: discord.Interaction) -> None:
        uid = str(interaction.user.id)
        user, is_new = self.game_data.get_or_create_user(uid)

        if is_new:
            await interaction.response.send_message(NEW_ACCOUNT_MESSAGE)
            return

        if len(user.decks) >= 10:
            await interaction.response.send_message("You already have the maximum of 10 decks.")
            return

        user_cards = user.owned_cards
        distinct_characters = {owned.character_name for owned in user_cards}

        if len(distinct_characters) < 4:
            await interaction.response.send_message(
                "You do not have enough distinct characters (4+) to form a deck."
            )
            return

        view = DeckAddView(user_cards, uid, self.game_data)
        await interaction.response.send_message(
            "Select 4 unique characters for your new deck:", view=view
        )

    @app_commands.command(name="delete", description="Delete one of your decks.")
    async def delete_deck(self, interaction: discord.Interaction) -> None:
        uid = str(interaction.user.id)
        user = self.game_data.get_user(uid)

        if not user.decks:
            await interaction.response.send_message("You have no decks to delete.")
            return

        decks = user.decks
        view = DeleteDeckView(uid, self.game_data, decks)

        await interaction.response.send_message(content="Select a deck to delete:", view=view)

    @app_commands.command(name="edit", description="Edit one of your existing decks.")
    async def edit_deck(self, interaction: discord.Interaction) -> None:
        uid = str(interaction.user.id)
        user = self.game_data.get_user(uid)

        if not user.decks:
            await interaction.response.send_message("You have no decks to edit.")
            return

        decks = user.decks
        view = EditDeckView(uid, self.game_data, decks)

        await interaction.response.send_message("Select a deck to edit:", view=view)


async def setup(bot: PearlBot) -> None:
    await bot.add_cog(Decks(bot, bot.game_data))
