from nextcord.ext.commands import Bot

from bot.cogs.util import register_util_cog
from bot.cogs.music import register_music_cog


def register_all_cogs(bot: Bot) -> None:
    bot.load_extension('onami')
    cogs = (
        register_util_cog,
        register_music_cog,
    )
    for cog in cogs:
        cog(bot)