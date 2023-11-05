from nextcord.ext import commands
from newkbot.config import MusicConfig

from mafic import NodePool

from typing import Any

class Bot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.ready_ran = False
        self.pool = NodePool(self)

    async def on_ready(self):
        if self.ready_ran:
            return

        await self.pool.create_node(
            host=MusicConfig.HOST,
            port=MusicConfig.PORT,
            label=MusicConfig.LABEL,
            password=MusicConfig.PASSWORD,
        )

        self.ready_ran = True