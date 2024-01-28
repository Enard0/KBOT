from requests import get
from nextcord import Interaction


async def ytSearch(cog, interaction: Interaction, query: str):
    await interaction.response.defer()
    await interaction.response.send_autocomplete(
        get(
            "http://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q="
            + query
        ).json()[1]
    )
