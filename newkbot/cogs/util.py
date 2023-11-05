from nextcord.ext.commands import Cog, Context
from nextcord import Interaction, Member, slash_command

import traceback

from newkbot.abstracts import Bot

import time

class __UtilCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        print(f'cog {self.__class__.__name__} loaded')

    @slash_command(dm_permission=False)
    async def ping(self,inter: Interaction[Bot]):
        '''Opóźnienie bota.'''
        assert isinstance(inter.user, Member)

        before = time.monotonic()
        message = await inter.send(f"Pong.")
        ping = (time.monotonic() - before) * 1000
        try:
            await message.edit(content=f":ping_pong: Gateway: {str(self.bot.latency*1000).split('.')[0]}ms\n:ping_pong: Bot: {int(ping)}ms")
        except:
            await message.edit('Nie wiem')

    @Cog.listener()
    async def on_application_command_error(self,inter: Interaction[Bot], error: Exception):
        traceback.print_exception(type(error), error, error.__traceback__)
        await inter.send(f"Wystąpił nieoczekiwany błąd: {error}")


def register_util_cog(bot: Bot) -> None:
    bot.add_cog(__UtilCog(bot))