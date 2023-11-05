from nextcord.ext.commands import Cog, Context
from nextcord import Interaction, Member, slash_command, Interaction, Member, Embed, Color

from newkbot.models import Bot, Select_Song_Button, KPlayer

from mafic import Playlist, Track, TrackEndEvent, SearchType

from nextcord.ui import Button, View

class __MusicCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        print(f'cog {self.__class__.__name__} loaded')

    @slash_command(dm_permission=False)
    async def join(self,inter: Interaction[Bot]):
        """Join your voice channel."""
        assert isinstance(inter.user, Member)

        if not inter.user.voice or not inter.user.voice.channel:
            return await inter.response.send_message("Nie jesteś połączony z kanałem głosowym.", ephemeral=True)
        
        channel = inter.user.voice.channel

        if inter.guild.voice_client:
            if inter.guild.voice_client.channel == channel:
                return await inter.response.send_message("Bot jest już na kanale z tobą UwU.", ephemeral=True)
            else:
                await inter.guild.voice_client.move_to(channel)  # pyright: ignore[reportGeneralTypeIssues]
                return await inter.send(f"Przełączono do {channel.mention}.",delete_after=5)

        await channel.connect(cls=KPlayer)  # pyright: ignore[reportGeneralTypeIssues]
        await inter.send(f"Dołaczono do {channel.mention}.",delete_after=5)

    @slash_command(dm_permission=False)
    async def leave(self,inter: Interaction[Bot]):
        """Leave current voice channel."""
        assert isinstance(inter.user, Member)

        if not inter.guild.voice_client:
            return await inter.response.send_message("Bota nie ma na kanale głosowym.", ephemeral=True)
        
        # This apparently **must** only be `Client`.
        channel = inter.guild.voice_client.channel
        await inter.guild.voice_client.disconnect()  # pyright: ignore[reportGeneralTypeIssues]
        await inter.send(f"Rozłączono z {channel.mention}.",delete_after=5)

    @slash_command(dm_permission=False)
    async def play(self, inter: Interaction[Bot], query: str):
        """Play a song.

        query:
            The song to search or play.
        """
        assert inter.guild is not None

        if not inter.user.voice or not inter.user.voice.channel:
            return await inter.response.send_message("Połącz się z kanałem głosowym", ephemeral=True)
    
        if not inter.guild.voice_client:
            await self.join(inter)

        if not inter.guild.voice_client.channel == inter.user.voice.channel:
            return await inter.response.send_message("Bot jest na innym kanale. Uzyj /join aby przenieść", ephemeral=True)

        player: KPlayer = (
            inter.guild.voice_client
        )

        tracks = await player.fetch_tracks(query)

        if not tracks:
            return await inter.send("No tracks found.")

        if isinstance(tracks, Playlist):
            tracks = tracks.tracks
            if len(tracks) > 1:
                player.queue.extend(tracks)

        else:
            if len(tracks)>1:
                view = View(timeout=30, auto_defer=False)
                embed = Embed(color=Color.magenta(),title='Wybierz utwór:')
                for i, track in enumerate(tracks[:5]):
                    view.add_item(Select_Song_Button(i,track.uri))
                    embed.add_field(name=f'{i+1}.',value=f'{track.title}',inline=False)
                    embed.add_field(name=" ",value=" ",inline=False)
                return await inter.send(embed=embed, view=view, ephemeral=True)

        track = tracks[0]
        if
        await player.play(track)

        await inter.send(f"Playing {track}")
    @Cog.listener()
    async def on_track_end(event: TrackEndEvent):
        assert isinstance(event.player, KPlayer)

        if event.player.queue:
            await event.player.play(event.player.queue.pop(0))
    


def register_music_cog(bot: Bot) -> None:
    bot.add_cog(__MusicCog(bot))