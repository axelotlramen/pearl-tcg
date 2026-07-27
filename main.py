from __future__ import annotations

from pearl_tcg.bot import PearlBot
from pearl_tcg.config import CONFIG

bot = PearlBot()


bot.run(CONFIG.discord_token)
