from nextcord.ext.commands import Cog
from datetime import datetime
from nextcord import (
    Interaction,
    Member,
    slash_command,
    Embed,
    Color,
    SlashOption,
)
import re
from bot.config import BotConfig

from typing import Optional

from bot.models import Bot, KPlayer, buttons, decorators, autocomplete

from mafic import Playlist, TrackEndEvent, EndReason

from nextcord.ui import View
from os import path


class __MusicCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.playlistusers = dict()
        self.playlistguilds = dict()
        if not path.isfile(BotConfig.LOCATION + "index.conf"):
            self.playlists = False
            return

        with open(BotConfig.LOCATION + "index.conf", "r") as file:
            for line in file:
                if path.isfile(BotConfig.LOCATION + line):
                    with open(BotConfig.LOCATION + line, "r") as file2:
                        file2.readline()
                        owner = file2.readline().split("\n")[0]
                        if owner in self.playlistusers:
                            self.playlistusers[owner][0].append(line)
                        else:
                            self.playlistusers[owner] = [[line], []]
                        users = file2.readline().split("\n")[0].split(";")[:-1]
                        for user in users:
                            if user in self.playlistusers:
                                self.playlistusers[user][1].append(line)
                            else:
                                self.playlistusers[user] = [[], [line]]
                        guilds = file2.readline().split("\n")[0].split(";")[:-1]
                        for guild in guilds:
                            if guild in self.playlistguilds:
                                self.playlistguilds[guild].append(line)
                            else:
                                self.playlistguilds[guild] = [line]
        self.playlists = True

    @Cog.listener()
    async def on_ready(self) -> None:
        print(f"cog {self.__class__.__name__} loaded")

    @slash_command(dm_permission=False)
    async def join(self, inter: Interaction[Bot]):
        """Join your voice channel."""
        assert isinstance(inter.user, Member)

        if not inter.user.voice or not inter.user.voice.channel:
            return await inter.response.send_message(
                "Nie jesteś połączony z kanałem głosowym.", ephemeral=True
            )

        channel = inter.user.voice.channel

        if inter.guild.voice_client:
            if inter.guild.voice_client.channel == channel:
                return await inter.response.send_message(
                    "Bot jest już na kanale z tobą UwU.", ephemeral=True
                )
            else:
                await inter.guild.voice_client.move_to(channel)
                return await inter.send(
                    f"Przełączono do {channel.mention}.", delete_after=5
                )

        await channel.connect(cls=KPlayer)
        await inter.send(f"Dołaczono do {channel.mention}.", delete_after=5)

    @slash_command(dm_permission=False)
    async def leave(self, inter: Interaction[Bot]):
        """Leave current voice channel."""
        assert isinstance(inter.user, Member)

        if not inter.guild.voice_client:
            return await inter.response.send_message(
                "Bota nie ma na kanale głosowym.", ephemeral=True
            )

        channel = inter.guild.voice_client.channel
        await inter.guild.voice_client.disconnect()
        await inter.send(f"Rozłączono z {channel.mention}.", delete_after=5)

    @slash_command(dm_permission=False)
    async def play(
        self,
        inter: Interaction[Bot],
        query: str = SlashOption(
            name="query",
            autocomplete=True,
            autocomplete_callback=autocomplete.ytSearch,
        ),
        special: str = SlashOption(
            name="special",
            required=False,
            choices=["force", "force skip"],
        ),
    ):
        """Play a song.

        query:
          The song to search or play.
        """
        assert inter.guild is not None

        if not inter.user.voice or not inter.user.voice.channel:
            return await inter.response.send_message(
                "Połącz się z kanałem głosowym", ephemeral=True
            )

        if not inter.guild.voice_client:
            await self.join(inter)

        if not inter.guild.voice_client.channel == inter.user.voice.channel:
            return await inter.response.send_message(
                "Bot jest na innym kanale. Uzyj /join aby przenieść",
                ephemeral=True,
            )

        player: KPlayer = inter.guild.voice_client

        tracks = await player.fetch_tracks(query)

        if not tracks:
            return await inter.send("No tracks found.")

        if isinstance(tracks, Playlist):
            tracks = tracks.tracks
            errs = 0
            for track in tracks:
                for i in range(len(player.queue)):
                    if player.queue[i].uri == track.uri:
                        if player.shuffle == 2 or i >= player.pos:
                            errs += 1
                            break
                        player.queue.pop(i)
                        player.pos -= 1
                else:
                    player.queue.append(track)
            embed = Embed(
                color=Color.dark_green(),
                title=f"Poprawnie dodano {len(tracks)-errs} utwórów, {errs} już występuje",
                description=f"[{track.title}]({track.uri})",
                timestamp=datetime.now(),
            )
            embed.set_author(name=inter.user, icon_url=inter.user.avatar)
            embed.set_thumbnail(track.artwork_url)
            return await inter.send(embed=embed)

        else:
            if len(tracks) > 1:
                view = View(timeout=30, auto_defer=False)
                embed = Embed(color=Color.magenta(), title="Wybierz utwór:")
                for i, track in enumerate(tracks[:5]):
                    view.add_item(buttons.SelectSong(i + 1, track.uri))
                    embed.add_field(
                        name=f"{i+1}.", value=f"{track.title}", inline=False
                    )
                    embed.add_field(name=" ", value=" ", inline=False)
                return await inter.send(
                    embed=embed, view=view, ephemeral=True, delete_after=30
                )
            else:
                track = tracks[0]
                for i in range(len(player.queue)):
                    if player.queue[i].uri == track.uri:
                        if player.shuffle == 2 or i >= player.pos:
                            return await inter.send(
                                "Utwór już jest dodany", ephemeral=True
                            )
                        player.queue.pop(i)
                        player.pos -= 1
                player.queue.append(track)
                embed = Embed(
                    color=Color.dark_green(),
                    title="Dodano utwór:",
                    description=f"[{track.title}]({track.uri})",
                    timestamp=datetime.now(),
                )
                embed.set_author(name=inter.user, icon_url=inter.user.avatar)
                embed.set_thumbnail(track.artwork_url)
                await inter.send(embed=embed)

        if not player.current:
            await player.play_next()

    @slash_command(dm_permission=False)
    @decorators.joinedVc()
    async def skip(
        self,
        inter: Interaction[Bot],
        pos: int = SlashOption(
            required=False,
            default=None,
        ),
    ):
        """Pomiń obecny utwór, lub kilka utworów."""
        player: KPlayer = inter.guild.voice_client
        if pos is not None:
            if pos < 0 and player.pos + pos < 1:
                return await inter.send(
                    f"""nie można cofnąć o {-pos}.
Maksymalnie można cofnąć o {player.pos-1}"""
                )
            if pos > len(player.queue) - player.pos:
                return await inter.send(
                    f"""Nie można pominąć o {pos} utworów.
Maksymalnie można pominąć {len(player.queue)-player.pos}""",
                    ephemeral=True,
                )
            if await player.play_next(player.pos + pos):
                return await inter.send(
                    embed=Embed(
                        color=Color.dark_magenta(), title="Pominięto o " + str(pos)
                    )
                )
            return await inter.send("Wystąpił błąd")
        if await player.play_next():
            return await inter.send(
                embed=Embed(color=Color.dark_magenta(), title="Pominięto")
            )
        return await inter.send("Kolejka jest pusta")

    @slash_command(dm_permission=False)
    @decorators.joinedVc()
    async def jump(
        self,
        inter: Interaction[Bot],
        to: int = SlashOption(
            required=True,
            default=None,
            min_value=-1,
        ),
    ):
        """Przeskocz do pozycji."""
        player: KPlayer = inter.guild.voice_client
        if to == 0:
            to = 1
        if to == -1:
            if await player.play_next(len(player.queue)):
                return await inter.send(
                    embed=Embed(
                        color=Color.dark_magenta(),
                        title=f"Przeskoczono do  pozycji {len(player.queue)}",
                    )
                )
            return await inter.send("Kolejka jest pusta")
        if await player.play_next(to):
            return await inter.send(
                embed=Embed(
                    color=Color.dark_magenta(),
                    title=f"Przeskoczono do pozycji {to}",
                )
            )

        return await inter.send("Nie można przewinąć do tej pozycji")

    @slash_command(dm_permission=False)
    @decorators.joinedVc()
    async def queue(self, inter: Interaction[Bot]):
        """Wyświetl kolejkę utworów."""
        player: KPlayer = inter.guild.voice_client
        if len(player.queue) == 0:
            return await inter.send("Kolejka jest pusta")
        startpos = int(player.pos / 10) * 10
        o = "```\n"
        endpos = min(10, len(player.queue) - startpos)
        for i in range(endpos):
            if startpos + endpos in (10, 100, 1000) and i != 9:
                o += " "
            o += (
                f"{str(startpos + i+1)})  {player.queue[startpos + i].title}\n\n"
                if startpos + i + 1 != player.pos
                else f"""    ⬐ == Obecnie odtwarzane ==
{str(startpos + i+1)})  {player.queue[startpos + i].title}
    ⬑ ========================\n\n"""
            )
        embed = Embed(
            title="Kolejka utworów",
            description=o + "```",
        )
        embed.set_footer(
            text=f"""🔁 Zapętlenie: {'✅ włączone' if player.loop else '❌ wyłączone'}
🔀Przemieszanie: {'✅ włączone' if player.shuffle else '❌ wyłączone'}"""
        )
        view = View(timeout=None, auto_defer=False)
        view.add_item(buttons.QueuePage("Prev", startpos - 10, startpos - 10 < 0))
        view.add_item(
            buttons.QueuePage("Next", startpos + 10, startpos + 10 >= len(player.queue))
        )
        return await inter.send(embed=embed, view=view)

    @slash_command(dm_permission=False)
    @decorators.joinedVc()
    async def loop(
        self,
        inter: Interaction[Bot],
        _set: Optional[bool] = SlashOption(name="set", required=False),
    ):
        """Ustaw zapętlanie."""
        player: KPlayer = inter.guild.voice_client
        if _set is None:
            player.loop = ~player.loop
            if player.loop:
                return await inter.send(
                    embed=Embed(color=Color.dark_teal(), title="Włączono zapętlenie")
                )
            return await inter.send("Wyłączono zapętlenie")

    @slash_command(dm_permission=False)
    @decorators.joinedVc()
    async def shuffle(
        self,
        inter: Interaction[Bot],
        _set: str = SlashOption(
            name="set",
            required=False,
            choices=["0 off", "1 once", "2 each", "3 next"],
        ),
    ):
        """Ustaw tryb przemieszania."""
        player: KPlayer = inter.guild.voice_client
        if _set is None:
            player.shuffle += 3
            if player.shuffle > 3:
                player.shuffle = 0
        else:
            player.shuffle = int(_set[0])
        match player.shuffle:
            case 0:
                text = "Wyłączono przemieszanie kolejki"
            case 1:
                text = "Przemieszanie kolejki: przy loopie"
            case 2:
                text = "Przemieszanie kolejki: każdy utwór losowo"
            case 3:
                text = "Przemieszanie kolejki: kolejny utwór losowo"
        embed = Embed(
            color=Color.dark_teal(),
            title=text,
            description="",
            timestamp=datetime.now(),
        )
        embed.set_author(name=inter.user, icon_url=inter.user.avatar)
        return await inter.send(embed=embed)

    @slash_command(dm_permission=False)
    @decorators.joinedVc()
    async def clear(self, inter: Interaction[Bot]):
        """Wyczyść kolejke utworów."""
        player: KPlayer = inter.guild.voice_client
        if len(player.queue) == 0:
            return await inter.send("Kolejka jest już pusta", ephemeral=True)
        view = View(timeout=30, auto_defer=False)
        view.add_item(buttons.ClearQueue())
        embed = Embed(
            color=Color.dark_red(),
            title="Czy chcesz wyczyścić kolejkę?",
            description="",
            timestamp=datetime.now(),
        )
        embed.set_footer(
            text="Tej akcji nie można cofnąć",
        )
        embed.set_author(name=inter.user, icon_url=inter.user.avatar)
        await inter.send(embed=embed, view=view, ephemeral=True, delete_after=30)

    @slash_command(dm_permission=False)
    @decorators.joinedVc()
    async def remove(
        self,
        inter: Interaction[Bot],
        pos: int = SlashOption(
            required=True,
            default=None,
            min_value=-1,
        ),
    ):
        """Wyczyść kolejke utworów."""
        player: KPlayer = inter.guild.voice_client
        if pos == 0:
            pos = 1
        if pos == -1:
            pos = len(player.queue)
        if len(player.queue) < pos:
            return await inter.send("Kolejka jest już pusta", ephemeral=True)
        view = View(timeout=30, auto_defer=False)
        view.add_item(buttons.RemoveQueue(pos - 1))
        track = player.queue[pos - 1]
        embed = Embed(
            color=Color.dark_red(),
            title="Czy chcesz usunąć ten utwór?",
            description=f"[{track.title}]({track.uri})",
            timestamp=datetime.now(),
        )
        embed.set_footer(
            text="Tej akcji nie można cofnąć",
        )
        embed.set_author(name=inter.user, icon_url=inter.user.avatar)
        embed.set_thumbnail(track.artwork_url)
        await inter.send(embed=embed, view=view, ephemeral=True, delete_after=30)

    @slash_command(dm_permission=False)
    @decorators.joinedVc()
    async def save(self, inter: Interaction[Bot], name: str):
        """Zapisz kolejke utworów pod podaną nazwą."""
        player: KPlayer = inter.guild.voice_client
        if not self.playlists:
            return await inter.send(
                "Wystąpił błąd przy zapisywaniu playlist. Nie zadziała. Admin chuj"
            )
        if not re.match("^[A-Za-z0-9_-]*$", name):
            return await inter.send(
                "Niedozwolone znaki. Dozwolone duże małe litery, cyfry, `-` `_`",
                ephemeral=True,
            )
        with open(BotConfig.LOCATION + "index.conf", "r") as file:
            if (
                name + inter.user.id in file.readlines
                or name + inter.user.id + "\n" in file.readlines
            ):
                return await inter.send(
                    "Masz już zapisaną playliste o takiej nazwie", ephemeral=True
                )
        with open(BotConfig.LOCATION + "index.conf", "a") as file:
            file.write(name + "\n")
        with open(BotConfig.LOCATION + name + inter.user.id, "w") as file:
            file.writelines(
                [
                    name,
                    inter.user.id,
                    inter.user.id,
                    inter.guild_id,
                    "\n",
                ]
            )
            for track in player.queue:
                file.write(track.uri + ";")

        embed = Embed(
            color=Color.dark_green(),
            title="Zapisano",
            description=name,
            timestamp=datetime.now(),
        )
        embed.set_author(name=inter.user, icon_url=inter.user.avatar)
        return await inter.send(embed=embed)

    @Cog.listener()
    async def on_track_end(self, event: TrackEndEvent):
        assert isinstance(event.player, KPlayer)
        if event.reason == EndReason.REPLACED:
            return
        await event.player.play_next()


def register_music_cog(bot: Bot) -> None:
    bot.add_cog(__MusicCog(bot))
