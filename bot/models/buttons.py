from nextcord.ui import Button
from datetime import datetime
from nextcord import ButtonStyle, Interaction, Embed, Color
from .player import KPlayer


class buttons:
    class SelectSong(Button):
        def __init__(self, label, uri):
            super().__init__(
                custom_id=uri,
                label=label,
                style=ButtonStyle.blurple,
            )

        async def callback(self, interaction: Interaction):
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
                color=Color.purple(),
                title="Dodano utwór:",
                description=f"[{track.title}]({track.uri})",
                timestamp=datetime.now(),
            )
            embed.set_author(name=interaction.user, icon_url=interaction.user.avatar)
            embed.set_thumbnail(track.artwork_url)
            await interaction.send(embed=embed)
            player.queue.append(track)

            if not player.current:
                await player.play_next()
