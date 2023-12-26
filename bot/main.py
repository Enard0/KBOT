from nextcord import Intents

from bot.config import BotConfig
from bot.cogs import register_all_cogs
from bot.models import Bot

from logging import DEBUG, getLogger

getLogger("mafic").setLevel(DEBUG)


def start_bot():
    intents = Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.voice_states = True
    intents.members = True

    bot = Bot(
        BotConfig.CMD_PREFIX,
        intents=intents,
        default_guild_ids=[801198165428535316, 758418616021811290],
    )

    register_all_cogs(bot)

    bot.run(BotConfig.TOKEN)
