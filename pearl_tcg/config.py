"""
Copied and Edited from Hoyo-Buddy Config File: https://github.com/seriaati/hoyo-buddy/blob/main/hoyo_buddy/config.py
"""

from __future__ import annotations

from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

type EnvType = Literal["dev", "test", "prod"]
type Deployment = Literal["main", "sub"]


class Config(BaseSettings):
    # Discord
    discord_token: str
    test_guild_id: int

    # file routes
    user_data_file: str
    card_root: str

    env: EnvType = "dev"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def is_dev(self) -> bool:
        return self.env == "dev"


load_dotenv()
CONFIG = Config()  # pyright: ignore[reportCallIssue]
