from __future__ import annotations

import discord
from discord.ui import View


class BaseView(View):
    def __init__(self, *, timeout: float = 60) -> None:
        super().__init__(timeout=timeout)
        self.message: discord.Message | None = None

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
