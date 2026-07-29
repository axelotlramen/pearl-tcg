from __future__ import annotations

from collections import Counter, defaultdict
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from pearl_tcg.constants import AVAILABLE_BORDERS, CONDITION_UPGRADE_COST, NEW_ACCOUNT_MESSAGE
from pearl_tcg.enums import CardCondition, Path
from pearl_tcg.models.cards import Card
from pearl_tcg.views.cards.card_album_view import CardAlbumPaginator
from pearl_tcg.views.cards.upgrade_confirm_view import UpgradeConfirmView

if TYPE_CHECKING:
    from pearl_tcg.bot import PearlBot
    from pearl_tcg.models.game_data import GameData
    from pearl_tcg.models.user import TCGUser

_BORDER_CHOICES = [app_commands.Choice(name=border, value=border) for border in AVAILABLE_BORDERS]


def _owned_card_choices(
    user: TCGUser, current: str, *, exclude_mint: bool
) -> list[app_commands.Choice[str]]:
    choices: list[app_commands.Choice[str]] = []
    for owned in user.owned_cards:
        if exclude_mint and owned.condition == CardCondition.MINT:
            continue
        label = f"{owned.character_name} {owned.rarity}★ {owned.condition.name.title()}"
        if current.lower() in label.lower():
            choices.append(app_commands.Choice(name=label[:100], value=owned.id))
    return choices[:25]


class Cards(commands.GroupCog, name="cards"):
    border = app_commands.Group(name="border", description="Manage the cosmetic border on a card.")

    def __init__(self, bot: commands.Bot, game_data: GameData) -> None:
        self.bot = bot
        self.game_data = game_data

    @app_commands.command(name="my", description="Summarize a user's card collection.")
    async def list_user_cards(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        uid = str(interaction.user.id)
        user, is_new = self.game_data.get_or_create_user(uid)

        if is_new:
            await interaction.followup.send(NEW_ACCOUNT_MESSAGE)
            return

        if not user.owned_cards:
            await interaction.followup.send(
                "You don't own any cards yet. Cards will be claimable soon."
            )
            return

        best_rarity: dict[str, int] = {}
        counts: Counter[str] = Counter()
        for owned in user.owned_cards:
            counts[owned.character_name] += 1
            best_rarity[owned.character_name] = max(
                best_rarity.get(owned.character_name, 0), owned.rarity
            )

        embed = discord.Embed(
            title=f"{interaction.user.display_name}'s Card Collection", color=discord.Color.green()
        )
        for name in sorted(counts):
            embed.add_field(
                name=name,
                value=f"Owned: {counts[name]} · Best: {best_rarity[name]}★",
                inline=True,
            )
        embed.set_footer(text="Use /cards album to see and manage individual cards.")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="all", description="List all available cards.")
    async def list_all_cards(self, interaction: discord.Interaction) -> None:
        cards = self.game_data.cards
        if not cards:
            await interaction.response.send_message("No cards found.", ephemeral=True)
            return

        cards_by_path: dict[Path, list[Card]] = defaultdict(list)
        for card in cards.values():
            cards_by_path[card.path].append(card)

        embed = discord.Embed(
            title="All Available Cards",
            description="Here's a list of all cards and their elements:",
            color=discord.Color.blurple(),
        )

        for path in sorted(cards_by_path.keys()):
            card_lines = [
                f"• **{card.name}** — {card.element.value}"
                for card in sorted(cards_by_path[path], key=lambda c: c.name)
            ]
            embed.add_field(name=f"{path.value} Cards", value="\n".join(card_lines), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="album", description="Browse your cards individually.")
    async def list_all_cards_album(self, interaction: discord.Interaction) -> None:
        cards = self.game_data.cards
        if not cards:
            await interaction.response.send_message("No cards found.")
            return

        uid = str(interaction.user.id)
        user = self.game_data.get_user(uid)

        if not user.owned_cards:
            await interaction.response.send_message(
                "You don't own any cards yet. Cards will be claimable soon."
            )
            return

        view = CardAlbumPaginator(user.owned_cards, cards, uid, self.game_data)
        await interaction.response.send_message(embed=view.get_embed(), view=view)
        view.message = await interaction.original_response()

    @app_commands.command(
        name="upgrade", description="Grind a card's condition up one step using materials."
    )
    @app_commands.describe(instance="Which card to upgrade")
    async def upgrade(self, interaction: discord.Interaction, instance: str) -> None:
        uid = str(interaction.user.id)
        user = self.game_data.get_user(uid)
        owned = self.game_data.get_owned_card(uid, instance)

        if owned is None:
            await interaction.response.send_message(
                "Couldn't find that card in your collection.", ephemeral=True
            )
            return
        if owned.condition == CardCondition.MINT:
            await interaction.response.send_message("That card is already Mint.", ephemeral=True)
            return

        cost = CONDITION_UPGRADE_COST[owned.condition]
        if user.materials < cost:
            await interaction.response.send_message(
                f"Not enough materials - need {cost}, you have {user.materials}.", ephemeral=True
            )
            return

        next_condition = CardCondition(owned.condition + 1)
        view = UpgradeConfirmView(uid, instance, self.game_data)
        await interaction.response.send_message(
            f"Upgrade **{owned.character_name}** ({owned.rarity}★) from "
            f"{owned.condition.name.title()} to {next_condition.name.title()} "
            f"for {cost} materials?",
            view=view,
            ephemeral=True,
        )

    @upgrade.autocomplete("instance")
    async def upgrade_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        user = self.game_data.get_user(str(interaction.user.id))
        return _owned_card_choices(user, current, exclude_mint=True)

    @border.command(name="set", description="Equip a border on one of your cards.")
    @app_commands.describe(instance="Which card to change", border="Which border to equip")
    @app_commands.choices(border=_BORDER_CHOICES)
    async def border_set(
        self,
        interaction: discord.Interaction,
        instance: str,
        border: app_commands.Choice[str],
    ) -> None:
        uid = str(interaction.user.id)
        owned = self.game_data.get_owned_card(uid, instance)

        if owned is None:
            await interaction.response.send_message(
                "Couldn't find that card in your collection.", ephemeral=True
            )
            return

        owned.border = border.value
        self.game_data.save_users()

        await interaction.response.send_message(
            f"**{owned.character_name}** ({owned.rarity}★) now uses the **{border.value}** border.",
            ephemeral=True,
        )

    @border_set.autocomplete("instance")
    async def border_set_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        user = self.game_data.get_user(str(interaction.user.id))
        return _owned_card_choices(user, current, exclude_mint=False)


async def setup(bot: PearlBot) -> None:
    await bot.add_cog(Cards(bot, bot.game_data))
