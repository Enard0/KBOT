from nextcord import Intents

from newkbot.config import BotConfig
from newkbot.cogs import register_all_cogs
from newkbot.abstracts import Bot

from logging import DEBUG, getLogger

getLogger("mafic").setLevel(DEBUG)

def start_bot():
    intents = Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.voice_states = True

    bot = Bot(BotConfig.CMD_PREFIX, intents=intents)

    register_all_cogs(bot)

    bot.run(BotConfig.TOKEN)