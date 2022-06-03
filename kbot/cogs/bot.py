import discord
from discord.ext import commands


class BotCog(commands.Cog, name='Inne'):
	"""BotCog"""

	def __init__(self, bot):
		self.bot = bot
		
	@commands.command(name="help",aliases=['pomoc'])
	async def helpcmd(self, ctx, *cmdhelp):
		'''Pomoc. !help [komenda]'''
		if cmdhelp == ():
			cogs = []
			cmdlist = []
			for cogcmd in self.bot.cogs:
				cogs.append(cogcmd)
			cogs.remove("Jishaku")
			for cog in cogs:
				cmds = []
				embed = discord.Embed(title=cog,colour=ctx.author.colour)
				for cmd in self.bot.walk_commands():
					if cmd.cog_name == cog and not cmd.name in cmdlist:
						if str(cmd.help) != "None":
							embed.add_field(name=cmd.name,value=cmd.help.split('.')[0],inline=True)
						else:
							embed.add_field(name=cmd.name,value=cmd.help,inline=True)
						cmdlist.append(cmd.name)
				embed.set_footer(text='Wpisz "!help <nazwa komendy>" aby uzyskać więcej informacji')
				await ctx.author.send(embed=embed)
			if ctx.channel != 'private':
				await ctx.send('Wysłano w wiadomości prywatnej')
		else:
			jest = False
			for cmd in self.bot.walk_commands():
				if (cmd.name.lower() == cmdhelp[0].lower() or cmdhelp[0].lower() in cmd.aliases) and jest == False:
					embed = discord.Embed(title=cmd.name+":",colour=ctx.author.colour,description=cmd.help.split('.')[0])
					embed.add_field(name='Użycie',value=cmd.help.split('.')[1],inline=False)
					if ', '.join(cmd.aliases)!='':
						embed.add_field(name='Aliasy',value=', '.join(cmd.aliases),inline=False)
					await ctx.send(embed=embed)
					jest = True
			if jest == False:
				await ctx.send('Nie ma takiej komendy!')


def setup(bot):
    bot.add_cog(BotCog(bot))
