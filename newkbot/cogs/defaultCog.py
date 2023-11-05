from nextcord.ext.commands import Bot, Cog, Context


class defaultCog(Cog):  
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        print(f'cog {self.__class__.__name__} loaded')