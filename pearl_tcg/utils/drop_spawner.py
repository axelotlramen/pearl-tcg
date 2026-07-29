from __future__ import annotations

import random
from typing import TYPE_CHECKING

from pearl_tcg.constants import DROP_MESSAGE_THRESHOLD_MAX, DROP_MESSAGE_THRESHOLD_MIN
from pearl_tcg.utils.drop_rolls import roll_rarity
from pearl_tcg.views.drop.drop_claim_view import DropClaimView, DropSlot, build_drop_embed

if TYPE_CHECKING:
    import discord

    from pearl_tcg.models.game_data import GameData

SLOTS_PER_DROP = 5


async def spawn_drop(channel: discord.abc.Messageable, game_data: GameData, guild_id: str) -> None:
    """Roll a new 5-card drop, reset the guild's message counter, and send the claim view."""
    state = game_data.get_guild_drop_state(guild_id)
    characters = list(game_data.cards.values())

    slots = [
        DropSlot(character_name=random.choice(characters).name, rarity=roll_rarity(state))
        for _ in range(SLOTS_PER_DROP)
    ]

    state.message_counter = 0
    state.next_drop_threshold = random.randint(
        DROP_MESSAGE_THRESHOLD_MIN, DROP_MESSAGE_THRESHOLD_MAX
    )
    game_data.save_guild_drop_states()

    view = DropClaimView(slots, game_data, guild_id)
    message = await channel.send(embed=build_drop_embed(slots), view=view)
    view.message = message
