from __future__ import annotations

import contextlib

import discord
from discord.ui import Button, Select, View


class BaseView(View):
    def __init__(self, *, timeout: float = 60) -> None:
        super().__init__(timeout=timeout)
        self.message: discord.Message | None = None

    async def on_timeout(self) -> None:
        for child in self.children:
            if isinstance(child, (Button, Select)):
                child.disabled = True

        if self.message is not None:
            with contextlib.suppress(discord.HTTPException):
                await self.message.edit(view=self)
