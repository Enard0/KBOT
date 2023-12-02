from nextcord.ui import Button
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
                await interaction.response.edit_message(
                    content=self.custom_id,
                    embed=None,
                    view=None,
                    delete_after=0.1,
                )
                track = await player.fetch_tracks(self.custom_id)
                track = track[0]
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
