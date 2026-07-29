from __future__ import annotations

import json
import pathlib

from pydantic import ValidationError

from pearl_tcg.config import CONFIG
from pearl_tcg.models.user import TCGUser
from pearl_tcg.utils.logger import LOGGER

USER_DATA_FILE = pathlib.Path(CONFIG.user_data_file)


def load_all_users() -> dict[str, TCGUser]:
    if not USER_DATA_FILE.exists():
        return {}
    raw_data = json.loads(USER_DATA_FILE.read_text(encoding="utf-8"))

    users: dict[str, TCGUser] = {}
    for uid, data in raw_data.items():
        try:
            users[uid] = TCGUser(**data)
        except ValidationError:
            LOGGER.warning("Skipping unmigratable user record %s (pre-instance-model schema)", uid)
            users[uid] = TCGUser()
    return users


def save_all_users(users: dict[str, TCGUser]) -> None:
    raw = {uid: user.model_dump(mode="json") for uid, user in users.items()}
    USER_DATA_FILE.write_text(json.dumps(raw, indent=4), encoding="utf-8")
