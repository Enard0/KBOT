from nextcord.ext.commands import Cog, Context
from nextcord import Interaction, Member, slash_command

from newkbot.abstracts import Bot

from mafic import Player, Playlist, Track, TrackEndEvent

from nextcord import Interaction, Member

from nextcord.abc import Connectable

class MyPlayer(Player[Bot]):
    def __init__(self, client: Bot, channel: Connectable) -> None:
        super().__init__(client, channel)

        # Mafic does not provide a queue system right now, low priority.
        self.queue: list[Track] = []

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
            return await inter.response.send_message("You are not in a voice channel.")

        channel = inter.user.voice.channel

        # This apparently **must** only be `Client`.
        await channel.connect(cls=MyPlayer)  # pyright: ignore[reportGeneralTypeIssues]
        await inter.send(f"Dołaczono do {channel.mention}.")

    @slash_command(dm_permission=False, guild_ids=[801198165428535316])
    async def leave(self,inter: Interaction[Bot]):
        """Leave current voice channel."""
        assert isinstance(inter.user, Member)

        if not inter.user.voice or not inter.user.voice.channel:
            return await inter.response.send_message("You are not in a voice channel.")

        channel = inter.user.voice.channel

        # This apparently **must** only be `Client`.
        await channel.connect(cls=MyPlayer)  # pyright: ignore[reportGeneralTypeIssues]
        await inter.send(f"Dołaczono do {channel.mention}.")

    @slash_command(dm_permission=False, guild_ids=[801198165428535316])
    async def play(self, inter: Interaction[Bot], query: str):
        """Play a song.

        query:
            The song to search or play.
        """
        assert inter.guild is not None

        if not inter.guild.voice_client:
            await self.join(inter)

        player: MyPlayer = (
            inter.guild.voice_client
        )  # pyright: ignore[reportGeneralTypeIssues]

        tracks = await player.fetch_tracks(query)

        if not tracks:
            return await inter.send("No tracks found.")

        if isinstance(tracks, Playlist):
            tracks = tracks.tracks
            if len(tracks) > 1:
                player.queue.extend(tracks[1:])

        track = tracks[0]

        await player.play(track)

        await inter.send(f"Playing {track}")
    


def register_music_cog(bot: Bot) -> None:
    bot.add_cog(__MusicCog(bot))