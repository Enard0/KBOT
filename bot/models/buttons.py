from nextcord.ui import Button, View
from datetime import datetime
from nextcord import ButtonStyle, Interaction, Embed, Color
from .player import KPlayer
from .checks import checks


class buttons:
    class SelectSong(Button):
        def __init__(self, label, uri):
            super().__init__(
                custom_id=uri,
                label=label,
                style=ButtonStyle.blurple,
            )

        async def callback(self, interaction: Interaction):
            if await checks.joinedVc(interaction):
                player: KPlayer = interaction.guild.voice_client
                track = await player.fetch_tracks(self.custom_id)
                track = track[0]
                for i in range(len(player.queue)):
                    if player.queue[i].uri == track.uri:
                        if player.shuffle == 2 or i >= player.pos:
                            return await interaction.send(
                                "Utwór już jest dodany", ephemeral=True
                            )
                        player.queue.pop(i)
                        player.pos -= 1
                await interaction.response.edit_message(
                    content=self.custom_id,
                    embed=None,
                    view=None,
                    delete_after=0.1,
                )
                embed = Embed(
                    color=Color.dark_green(),
                    title="Dodano utwór:",
                    description=f"[{track.title}]({track.uri})",
                    timestamp=datetime.now(),
                )
                embed.set_author(
                    name=interaction.user, icon_url=interaction.user.avatar
                )
                embed.set_thumbnail(track.artwork_url)
                player.queue.append(track)
                await interaction.send(embed=embed)

                if not player.current:
                    await player.play_next()

    class ClearQueue(Button):
        def __init__(self):
            super().__init__(
                label="Wyczyść",
                style=ButtonStyle.red,
            )

        async def callback(self, interaction: Interaction):
            if await checks.joinedVc(interaction):
                player: KPlayer = interaction.guild.voice_client
                await interaction.response.edit_message(
                    content="Wyczyszczono kolejke",
                    embed=None,
                    view=None,
                    delete_after=0.1,
                )
                embed = Embed(
                    color=Color.dark_red(),
                    title="Wyczyszczono kolejke",
                    description="",
                    timestamp=datetime.now(),
                )
                embed.set_author(
                    name=interaction.user, icon_url=interaction.user.avatar
                )
                player.queue = []
                player.pos = 0
                await interaction.send(embed=embed)

    class RemoveQueue(Button):
        def __init__(self, pos):
            self.pos = pos
            super().__init__(
                label="Usuń",
                style=ButtonStyle.red,
            )

        async def callback(self, interaction: Interaction):
            if await checks.joinedVc(interaction):
                player: KPlayer = interaction.guild.voice_client
                await interaction.response.edit_message(
                    content=f"Usunięto utwór z pozycji {self.pos+1}",
                    embed=None,
                    view=None,
                    delete_after=0.1,
                )
                track = player.queue.pop(self.pos)
                embed = Embed(
                    color=Color.dark_red(),
                    title=f"Usunięto utwór z pozycji {self.pos}:",
                    description=f"[{track.title}]({track.uri})",
                    timestamp=datetime.now(),
                )
                embed.set_author(
                    name=interaction.user.display_name, icon_url=interaction.user.avatar
                )
                embed.set_thumbnail(track.artwork_url)
                if player.pos > self.pos:
                    player.pos -= 1
                await interaction.send(embed=embed)

    class QueuePage(Button):
        def __init__(self, label, pos, disb):
            self.pos = pos
            super().__init__(
                label=label,
                style=ButtonStyle.blurple,
                disabled=disb,
            )

        async def callback(self, interaction: Interaction):
            if await checks.joinedVc(interaction):
                player: KPlayer = interaction.guild.voice_client
                view = View(timeout=None, auto_defer=False)
                view.add_item(
                    buttons.QueuePage("Prev", self.pos - 10, self.pos - 10 < 0)
                )
                view.add_item(
                    buttons.QueuePage(
                        "Next", self.pos + 10, self.pos + 10 >= len(player.queue)
                    )
                )
                o = "```\n"
                endpos = min(10, len(player.queue) - self.pos)
                for i in range(endpos):
                    if self.pos + endpos in (10, 100, 1000) and i != 9:
                        o += " "
                    o += (
                        f"{str(self.pos + i+1)})  {player.queue[self.pos + i].title}\n\n"
                        if self.pos + i + 1 != player.pos
                        else f"""    ⬐ == Obecnie odtwarzane ==
{str(self.pos + i+1)})  {player.queue[self.pos + i].title}
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
                await interaction.response.edit_message(
                    embed=embed,
                    view=view,
                )
