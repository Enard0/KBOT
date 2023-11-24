from nextcord.ui import Button
from nextcord import ButtonStyle, Interaction


class buttons:
    class SelectSong(Button):
        def __init__(self, label, uri):
            super().__init__(
                custom_id=uri,
                label=label,
                style=ButtonStyle.blurple,
            )

        async def callback(self, interaction: Interaction):
            player = interaction.guild.voice_client
            await interaction.response.edit_message(
                content=self.custom_id,
                embed=None,
                view=None,
                delete_after=1,
            )
            await interaction.send(content=self.custom_id)
            track = await player.fetch_tracks(self.custom_id)
            player.queue.append(track[0])

            if not player.current:
                await player.play(player.queue.pop(0))
