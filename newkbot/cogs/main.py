from nextcord.ext.commands import Bot

from newkbot.cogs.example import register_example_cogs


def register_all_cogs(bot: Bot) -> None:
    cogs = (
        register_example_cogs,
    )
    for cog in cogs:
        cog(bot)