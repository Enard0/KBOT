from nextcord.ext import application_checks
from nextcord import Interaction


class decorators:
    def joinedVc():
        async def predicate(inter: Interaction):
            if not inter.user.voice or not inter.user.voice.channel:
                await inter.send(
                    "Nie jesteś połączony z kanałem głosowym.", ephemeral=True
                )
                return False
            if (
                inter.guild.voice_client
                and inter.guild.voice_client.channel == inter.user.voice.channel
            ):
                return True
            await inter.send(
                "Najpierw dołącz bota używając /join",
                ephemeral=True,
            )
            return False

        return application_checks.check(predicate)


class checks:
    async def joinedVc(inter: Interaction):
        if not inter.user.voice or not inter.user.voice.channel:
            await inter.send("Nie jesteś połączony z kanałem głosowym.", ephemeral=True)
            return False
        if (
            inter.guild.voice_client
            and inter.guild.voice_client.channel == inter.user.voice.channel
        ):
            return True
        await inter.send(
            "Najpierw dołącz bota używając /join",
            ephemeral=True,
        )
        return False
