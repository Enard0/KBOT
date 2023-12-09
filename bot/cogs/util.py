from nextcord.ext.commands import Cog
from nextcord import Interaction, Member, slash_command, errors
from nextcord.ext import commands
import traceback

from bot.models import Bot

import time


class __UtilCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        print(f"cog {self.__class__.__name__} loaded")

    @slash_command(dm_permission=False)
    async def ping(self, inter: Interaction[Bot]):
        """Opóźnienie bota."""
        assert isinstance(inter.user, Member)

        before = time.monotonic()
        message = await inter.send("Pong.")
        ping = (time.monotonic() - before) * 1000
        try:
            await message.edit(
                content=f""":ping_pong: Gateway: {str(self.bot.latency*1000)
        .split('.')[0]}ms\n:ping_pong: Bot: {int(ping)}ms"""
            )
        except Exception:
            await message.edit("Nie wiem")

    @Cog.listener()
    async def on_application_command_error(
        self, inter: Interaction[Bot], error: Exception
    ):
        if (
            isinstance(error, commands.CommandNotFound)
            or isinstance(error, commands.CheckFailure)
            or isinstance(error, errors.ApplicationCheckFailure)
        ):
            pass
        elif not isinstance(error, str):
            traceback.print_exception(type(error), error, error.__traceback__)
            await inter.channel.send("Wystąpił nieoczekiwany błąd", delete_after=15)


def register_util_cog(bot: Bot) -> None:
    bot.add_cog(__UtilCog(bot))
