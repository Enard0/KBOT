from mafic import Player
from bot.models import Bot
from nextcord.abc import Connectable
from mafic import Track
from random import shuffle, randint


class KPlayer(Player[Bot]):
    def __init__(self, client: Bot, channel: Connectable) -> None:
        super().__init__(client, channel)

        # Mafic does not provide a queue system right now, low priority.
        self.queue: list[Track] = []
        self.pos: int = 0
        self.loop: bool = 0
        self.shuffle: int = 0

    async def move_to(self, channel: Connectable) -> None:
        await self.guild.change_voice_state(channel=channel)
        self.channel = channel

    async def play_next(self, position=None) -> bool:
        if not self.queue:
            return False
        if self.shuffle == 2:
            self.pos = randint(1, len(self.queue))
            await self.play(self.queue[self.pos - 1])
            return True
        if position is None:
            if len(self.queue) <= self.pos:
                if not self.loop:
                    return False
                if self.shuffle == 1:
                    shuffle(self.queue)
                if self.shuffle == 3:
                    track: Track = self.queue.pop(randint(0, len(self.queue) - 1))
                    self.queue.insert(0, track)
                await self.play(self.queue[0])
                self.pos = 1
                return True
            if self.shuffle == 3:
                track: Track = self.queue.pop(
                    randint(self.pos - 1, len(self.queue) - 1)
                )
                self.queue.insert(self.pos - 1, track)
            await self.play(self.queue[self.pos])
            self.pos += 1
            return True
        if position - 1 < 0 or position > len(self.queue):
            return False
        await self.play(self.queue[position - 1])
        self.pos = position
        return True
