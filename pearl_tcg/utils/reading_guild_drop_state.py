from __future__ import annotations

import json
import pathlib

from pearl_tcg.config import CONFIG
from pearl_tcg.models.guild_drop_state import GuildDropState

GUILD_DROP_STATE_FILE = pathlib.Path(CONFIG.guild_drop_state_file)


def load_all_guild_drop_states() -> dict[str, GuildDropState]:
    if not GUILD_DROP_STATE_FILE.exists():
        return {}
    raw_data = json.loads(GUILD_DROP_STATE_FILE.read_text(encoding="utf-8"))
    return {gid: GuildDropState(**data) for gid, data in raw_data.items()}


def save_all_guild_drop_states(states: dict[str, GuildDropState]) -> None:
    raw = {gid: state.model_dump(mode="json") for gid, state in states.items()}
    GUILD_DROP_STATE_FILE.write_text(json.dumps(raw, indent=4), encoding="utf-8")
