from mafic import Player
from bot.models import Bot
from nextcord.abc import Connectable
from mafic import Track

class KPlayer(Player[Bot]):
    def __init__(self, client: Bot, channel: Connectable) -> None:
        super().__init__(client, channel)

        # Mafic does not provide a queue system right now, low priority.
        self.queue: list[Track] = []
    
    async def move_to(self, channel: Connectable) -> None:
        await self.guild.change_voice_state(channel = channel)
        self.channel=channel