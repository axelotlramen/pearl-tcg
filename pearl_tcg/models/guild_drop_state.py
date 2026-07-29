from __future__ import annotations

import random

from pydantic import BaseModel, Field

from pearl_tcg.constants import DROP_MESSAGE_THRESHOLD_MAX, DROP_MESSAGE_THRESHOLD_MIN


def _random_threshold() -> int:
    return random.randint(DROP_MESSAGE_THRESHOLD_MIN, DROP_MESSAGE_THRESHOLD_MAX)


class GuildDropState(BaseModel):
    drop_channel_id: int | None = None
    message_counter: int = 0
    next_drop_threshold: int = Field(default_factory=_random_threshold)
    # Drops since the last 3-star-or-better/4-star-or-better/5-star-or-better hit in this guild.
    streak_3star: int = 0
    streak_4star: int = 0
    streak_5star: int = 0
