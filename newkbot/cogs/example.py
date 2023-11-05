from nextcord.ext.commands import Bot, Cog, Context

from .defaultCog import defaultCog

# todo: OtherCogs
class __MainOtherCog(defaultCog):
    pass

def register_example_cogs(bot: Bot) -> None:
    bot.add_cog(__MainOtherCog(bot))