from __future__ import annotations

import asyncio
import contextlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal

import discord
from discord.ui import Button

from durin_tcg.constants import EMBED_TIMEOUT, TURN_TIME_LIMIT
from durin_tcg.enums import CardAbility
from durin_tcg.views.base import BaseView

if TYPE_CHECKING:
    from durin_tcg.models.game import Battle, Player
    from durin_tcg.models.game_data import GameData


class BattleView(BaseView, ABC):
    def __init__(
        self,
        challenger: discord.User | discord.Member,
        opponent: discord.User | discord.Member | Literal["AI"],
        game: Battle,
        game_data: GameData,
        timeout: float = EMBED_TIMEOUT,
    ) -> None:
        super().__init__(timeout=timeout)
        self.challenger = challenger
        self.opponent = opponent
        self.game = game
        self.game_data = game_data

        self.challenger_turn = True  # challenger starts
        self.message: discord.Message | None = None
        self.turn_task: asyncio.Task | None = None

        self.add_item(BattleActionButton("Basic Attack", CardAbility.BASIC))
        self.add_item(BattleActionButton("Skill", CardAbility.SKILL))
        self.add_item(BattleActionButton("Ultimate", CardAbility.ULTIMATE))

        self.add_item(SwitchCharacterButton())

    def current_user(self) -> discord.User | discord.Member | str:
        return self.challenger if self.challenger_turn else self.opponent

    def current_player(self) -> Player:
        return self.game.player1 if self.challenger_turn else self.game.player2

    def enemy_player(self) -> Player:
        return self.game.player2 if self.challenger_turn else self.game.player1

    def build_embed(self, title: str, player: Player) -> discord.Embed:
        embed = discord.Embed(title=title)
        embed.add_field(name="", value=self.get_team_info_text(player), inline=False)
        return embed

    def get_team_info_text(self, player: Player) -> str:
        char_strings = []
        for char in player.deck:
            afflicted_elements_str = ", ".join(char.afflicted_elements)
            char_strings.append(
                f"{char.card.name} (HP: {char.current_hp})"
                + (afflicted_elements_str if char.afflicted_elements else "")
                + (" [Active]" if char == player.active_character else "")
            )
        return "\n".join(char_strings)

    async def update_ui(
        self, interaction: discord.Interaction, message: discord.Message | None = None
    ) -> None:
        message = message or self.message
        channel = message.channel if message else interaction.channel

        if message:
            with contextlib.suppress(discord.NotFound):
                await message.delete()

        user1_embed = self.build_embed(self.challenger.display_name, self.game.player1)

        opponent_name = (
            self.opponent if isinstance(self.opponent, str) else self.opponent.display_name
        )
        user2_embed = self.build_embed(opponent_name, self.game.player2)

        new_message = await channel.send(
            content=f"It's {self.current_user()}'s turn - {TURN_TIME_LIMIT} seconds left!",
            embeds=[user1_embed, user2_embed],
            view=self,
        )

        self.message = new_message

        self.start_turn_timer()

    def start_turn_timer(self) -> None:
        if self.turn_task and not self.turn_task.done():
            self.turn_task.cancel()

        self.turn_task = asyncio.create_task(self.turn_timer())

    async def turn_timer(self) -> None:
        try:
            for remaining in range(TURN_TIME_LIMIT, 0, -1):
                await asyncio.sleep(1)

                if self.message:
                    await self.message.edit(
                        content=f"It's {self.current_user()}'s turn - {remaining} seconds left!",
                        view=self,
                    )
        except asyncio.CancelledError:
            return

        if self.message:
            with contextlib.suppress(discord.NotFound):
                await self.message.edit(
                    content="Time's up! The battle has ended due to inactivity.", view=None
                )
        self.stop()

    async def take_turn(self, ability: CardAbility, interaction: discord.Interaction) -> None:
        if self.turn_task and not self.turn_task.done():
            self.turn_task.cancel()

        self.current_player().use_ability(ability, self.enemy_player())

        if self.enemy_player().active_character.current_hp <= 0:
            await self.end_battle(interaction)
            return

        self.challenger_turn = not self.challenger_turn

        await interaction.response.defer()

        await self.update_ui(interaction, self.message)

    async def end_battle(self, interaction: discord.Interaction) -> None:
        if self.turn_task and not self.turn_task.done():
            self.turn_task.cancel()

        await interaction.response.edit_message(content="someone won. not me though :(", view=None)
        self.stop()


class PlayerBattleView(BattleView):
    def __init__(
        self,
        challenger: discord.User | discord.Member,
        opponent: discord.User | discord.Member,
        game: Battle,
        game_data: GameData,
    ) -> None:
        super().__init__(challenger, opponent, game, game_data)


class AIBattleView(BattleView):
    def __init__(
        self, challenger: discord.User | discord.Member, game: Battle, game_data: GameData
    ) -> None:
        super().__init__(challenger, "AI", game, game_data)


class BattleActionButton(Button):
    def __init__(self, label: str, action: CardAbility) -> None:
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.action = action

    async def callback(self, interaction: discord.Interaction) -> None:
        view: BattleView = self.view  # pyright: ignore[reportAssignmentType]
        await view.take_turn(self.action, interaction)


class SwitchCharacterButton(Button):
    def __init__(self) -> None:
        super().__init__(label="Switch Character", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        view: BattleView = self.view  # pyright: ignore[reportAssignmentType]

        character_select_view = CharacterSelectView(view)
        await interaction.response.send_message(
            content="Choose a character to switch to:", view=character_select_view, ephemeral=True
        )


class CharacterSelectView(BaseView):
    def __init__(self, battle_view: BattleView) -> None:
        super().__init__(timeout=EMBED_TIMEOUT)
        self.battle_view = battle_view
        self.player = (
            battle_view.game.player1 if battle_view.challenger_turn else battle_view.game.player2
        )

        for i, char in enumerate(self.player.deck):
            if char != self.player.active_character:
                self.add_item(SingleCharacterButton(index=i, char_name=char.card.name))


class SingleCharacterButton(Button):
    def __init__(self, index: int, char_name: str) -> None:
        super().__init__(label=char_name, style=discord.ButtonStyle.primary)
        self.index = index

    async def callback(self, interaction: discord.Interaction) -> None:
        view: CharacterSelectView = self.view
        battle_view = view.battle_view
        player = view.player

        player.switch_character(self.index)

        await interaction.response.send_message(
            f"Switched to {player.active_character.card.name}!", ephemeral=True
        )

        await battle_view.update_ui(interaction)
