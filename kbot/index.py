from asyncio.tasks import wait, wait_for
import re
import discord
import os
from discord.ext import commands
import time
import sys, traceback
from discord_components import DiscordComponents, ComponentsBot, Button
import asyncio
from discord.utils import get
import jishaku

initial_extensions = ['cogs.music','cogs.bot','jishaku']

intents = discord.Intents().all()
bot = ComponentsBot(command_prefix = "-", intents=intents)#bot = commands.Bot(command_prefix='!',case_insensitive=True, description='MontarexBOT', intents=intents)
bot.remove_command('help')

if __name__ == '__main__':
	for extension in initial_extensions:
		try:
			bot.load_extension(extension)
		except:
			print("-" * 100)
			print(f"BŁĄD: MODUŁ {extension} NIE ZOSTAŁ ZAŁADOWANY\n\nERROR:\n")
			traceback.print_exc()

@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name="testy."))
	print(f'\n\nZalogowano jako:\n{bot.user.name} - {bot.user.id}\nWersja: {discord.__version__}\nServery: {len(bot.guilds)}')

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	await bot.process_commands(message)

@bot.event
async def on_command(ctx):
	await ctx.message.add_reaction('⌛')

@bot.event
async def on_command_completion(ctx):
	await ctx.message.add_reaction('✅')
	await ctx.message.remove_reaction('⌛',bot.user)


@bot.event
async def on_command_error(ctx, error):
	await ctx.message.add_reaction('❌')
	await ctx.message.remove_reaction('⌛',bot.user)
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send('Brakuje argumentu. Użyj komendy `-help komenda`, żeby dowiedzieć się jakie argumenty trzeba umieścić.')
	elif isinstance(error, commands.BotMissingPermissions):
		try:
			await ctx.send('⚠ BŁĄD ⚠\nNie mam wymaganych permisji')
		except:
			channel = ctx.author.id
			await channel.send('⚠ BŁĄD ⚠\nNie mam uprawnień do pisania na tamtym kanale')
	elif isinstance(error, commands.MissingPermissions):
		await ctx.send('nNie masz wymaganych permisji')
	elif isinstance(error, commands.NoPrivateMessage):
		await ctx.send('Ta komenda jest możliwa tylko na serwerze')
	elif isinstance(error, commands.DisabledCommand):
		await ctx.send('Ta komenda jest aktualnie wyłączona')
	elif isinstance(error, commands.CheckFailure):
		await ctx.send('Nie masz uprawnień do użycia komendy')
	elif isinstance(error, commands.CommandOnCooldown):
		await ctx.send('Musisz odczekać '+str(round(error.retry_after,1))+'s przed ponownym użyciem tej komendy')
	elif isinstance(error, commands.CommandNotFound):
		await ctx.message.remove_reaction('❌',bot.user)
	elif not isinstance(error, str):
		bot.cmdlog = discord.Webhook.partial(804717240129683487, 'YkuX8BiRTn4kyBhvSWo_sVLxR0rZfOWGVm0uLCmkeYA6z_WBLdvSCchtTyE3KuZJqFHG', adapter=discord.RequestsWebhookAdapter())
		channel = bot.get_channel(804717148705914900)
		await channel.send(f'Komenda: ```{ctx.message.content}``` Błąd: ```{error}```')
	else:
		pass

'''@bot.event
async def on_voice_state_update(member, before, after):
	if before.channel != None and before.channel != after.channel:
		for chan in before.channel:
			if chan not in after.channel:
				chn = chan
				break
		chn = before.channel
		player = bot.lavalink.player_manager.get(chn.guild.id)
		if len(chn.members)==1 and player and player.is_connected:
			def check(m, b, a):
				if b.channel != a.channel and a.channel==chn:
					return True
				return False
			try:
				await bot.wait_for('voice_state_update', timeout=60.0, check=check)
			except asyncio.TimeoutError:
				player.queue.clear()
				await player.stop()
				s = bot.get_channel(758418616021811294)
				await s.send('Wyebao mnie')
				await chn.guild.change_voice_state(channel=None)'''
		

'''
@bot.event
async def on_command_error(ctx, error):
    pass'''

bot.run(open('token.txt').read(), bot=True, reconnect=True)

