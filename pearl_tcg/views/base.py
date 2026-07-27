from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ui import Button, Select, View

if TYPE_CHECKING:
    import discord


class BaseView(View):
    def __init__(self, *, timeout: float = 60) -> None:
        super().__init__(timeout=timeout)
        self.message: discord.Message | None = None

    async def on_timeout(self) -> None:
        for child in self.children:
            if isinstance(child, (Button, Select)):
                child.disabled = True
