"""
This example cog demonstrates basic usage of Lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.
Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""
from asyncio.tasks import sleep
from math import fabs
import re

import discord
import lavalink
from discord.ext import commands
from discord_components import DiscordComponents, ComponentsBot, Button
import os.path
import asyncio

url_rx = re.compile(r'https?://(?:www\.)?.+')


class Music(commands.Cog, name='Muzyczne'):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            bot.lavalink = lavalink.Client(804715280361586748)
            bot.lavalink.add_node('127.0.0.1', 2333, 'VYTIftiyFIYVtvgbTVGHtyvguHRDTKF7itukhgYg', 'eu', 'default-node')  # Host, Port, Password, Region, Name
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        """ Cog unload handler. This removes any event hooks that were registered. """
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)
            # The above handles errors thrown in this cog and shows them to the user.
            # This shouldn't be a problem as the only errors thrown in this cog are from `ensure_voice`
            # which contain a reason string, such as "Join a voicechannel" etc. You can modify the above
            # if you want to do things differently.

    async def ensure_voice(self, ctx):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ('play','skip','disconnect','remove')
        if should_connect:
            if not ctx.author.voice or not ctx.author.voice.channel:
                # Our cog_command_error handler catches this and sends it to the voicechannel.
                # Exceptions allow us to "short-circuit" command invocation via checks so the
                # execution state of the command goes no further.
                raise commands.CommandInvokeError('Dołącz najpierw do kanału głosowego.')

            if not player.is_connected:
                if not should_connect:
                    raise commands.CommandInvokeError('Nie połączono.')

                permissions = ctx.author.voice.channel.permissions_for(ctx.me)

                if not permissions.connect or not permissions.speak:  # Check user limit too?
                    raise commands.CommandInvokeError('Potrzebuje uprawnień `CONNECT` oraz `SPEAK`.')

                player.store('channel', ctx.channel.id)
                await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)
            else:
                if int(player.channel_id) != ctx.author.voice.channel.id:
                    raise commands.CommandInvokeError('Musisz być na kanale głosowym ze mną.')

    async def track_hook(self, event):
        '''if isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            await guild.change_voice_state(channel=None)'''

    @commands.guild_only()
    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        """ Wyszukuje utwór i dodaje do kolejki. !play <link/nazwa na yt>"""
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip('<>')

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        # Get the results for the query from Lavalink.
        results = await player.node.get_tracks(query)

        # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
        # ALternatively, resullts['tracks'] could be an empty array if the query yielded no tracks.
        if not results or not results['tracks']:
            return await ctx.send('Nic nie znaleziono!')

        

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']
            corr=0
            for track in tracks:
                ex=False
                # Add all of the tracks from the playlist to the queue.
                for i in range(len(player.queue)):
                    if player.queue[i].uri == track['info']['uri']:
                        if i<player.pos:
                            player.pos-=1
                            await player.remove(i)
                            break
                        else:
                            ex=True
                            break
                if not ex:
                    player.add(requester=ctx.author.id, track=track)
                    corr+=1
            embed = discord.Embed(color=discord.Color.blurple())
            embed.title = 'Playlista dodana do kolejki!'
            embed.description = f'{results["playlistInfo"]["name"]} - {corr} utwórów'
            embed.set_footer(text=str(ctx.author))
        else:
            track = results['tracks'][0]
            # You can attach additional information to audiotracks through kwargs, however this involves
            # constructing the AudioTrack class yourself.
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            for i in range(len(player.queue)):
                if player.queue[i].uri == track['uri']:
                    if i<player.pos:
                        player.pos-=1
                        await player.remove(i)
                        break
                    else:
                        embed = discord.Embed(color=discord.Color.red())
                        embed.title = 'Utwór już występuje'
                        embed.description = f'[{track.title}]({track.uri})'
                        return await ctx.send(embed=embed)
            embed = discord.Embed(color=discord.Color.blurple())
            embed.description = f'[{track.title}]({track.uri})'
            player.add(requester=ctx.author.id, track=track)
            embed.set_footer(text=str(ctx.author))

        await ctx.send(embed=embed)


        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()
    
    @commands.guild_only()
    @commands.command(aliases=['q'])
    async def queue(self, ctx, *page):
        """Wyświetla kolejkę. !queue [strona]"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        try:
            pageid=int(page[0])
        except:
            pageid=player.pos//10
        queuesend = '```Strona '+str(pageid+1)+':\n'
        for idx, val in enumerate(player.queue[pageid*10:pageid*10+10],start=pageid*10):
            if idx +1 == player.pos:
                queuesend += '    ⬐ current track\n' + str(idx+1)+') '+val['title'] + '\n    ⬑ current track\n'# if idx<10 else str(idx) +')'+val['title'] + '\n    ⬑ current track\n'
            else:
                queuesend += ' '+str(idx+1)+') '+val['title'] + '\n' if idx<9 else str(idx+1)+') '+val['title'] + '\n'
        if pageid<1:
            btn1lock = True
        else:
            btn1lock = False
        if pageid*10>=len(player.queue)-12:
            btn2lock = True
        else:
            btn2lock = False
        if player.shuffle==0:
            shuff = 'Przemieszanie wyłączone'
        elif player.shuffle==1:
            shuff = 'Przemieszanie włączone (raz losowane)'
        elif player.shuffle==2:
            shuff = 'Przemieszanie włączone (każdy losowy)'
        elif player.shuffle==3:
            shuff = 'Przemieszanie włączone (bez powtórek)'
        else:
            shuff = 'co sie odwaliło wtf'
        lood = 'Zapętlanie włączone' if player.repeat else 'Zapętlanie wyłączone'
        await ctx.send(content=queuesend+'\n'+shuff+'\n'+lood+'```',
        components = [[
            Button(label = "Prev", custom_id = "0", style=1, disabled=btn1lock),
            Button(label = "Next", custom_id = "2", style=1, disabled=btn2lock)
        ]])

    @commands.guild_only()
    @commands.command()
    async def pause(self, ctx):
        """Wstrzymuje odtwarzanie utworu. !pause"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await player.set_pause(not player.paused)
        if player.paused:
            await ctx.send('Zatrzymano')
        else:
            await ctx.send('Wznowiono')

    @commands.guild_only()
    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        """Pomija utwór. !skip"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.current != None:
            embed = discord.Embed(color=discord.Color.blurple())
            embed.title = 'Skipped'
            track = player.current
            url = 'https://www.youtube.com/watch?v='+track["identifier"] if not 'http' in track["identifier"] else track["identifier"]
            embed.description = f'[{track["title"]}]({url})'
            await ctx.send(embed=embed)
            await player.skip()
            embed = discord.Embed(color=discord.Color.blurple())
            try:
                embed.title = 'Now playing'
                track = player.current
                url = 'https://www.youtube.com/watch?v='+track["identifier"] if not 'http' in track["identifier"] else track["identifier"]
                embed.description = f'[{track["title"]}]({url})'
                await ctx.send(embed=embed)
            except:
                pass
        else:
            await player.play()
            try:
                embed = discord.Embed(color=discord.Color.blurple())
                embed.title = 'Now playing'
                track = player.current
                url = 'https://www.youtube.com/watch?v='+track["identifier"] if not 'http' in track["identifier"] else track["identifier"]
                embed.description = f'[{track["title"]}]({url})'
                await ctx.send(embed=embed)
            except:
                pass
            #await ctx.send('bro WTF')
            
    @commands.guild_only()
    @commands.command()
    async def save(self, ctx, *, name: str):
        """Zapisuje playliste. !save <nazwa_zapisu>"""
        if os.path.exists(name):
            await ctx.send('Nazwa zajęta')
            return
        if name!='index.py' and '.' not in name:
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)
            out = []
            for i in player.queue:
                try:
                    out.append(i.identifier)
                except:
                    pass
            if out != []:
                with open("music/"+name,'w') as file:
                    file.write(';'.join(out))
        await ctx.send('Zapisano')

    @commands.guild_only()
    @commands.command()
    async def load(self, ctx, *, name: str):
        """Wczytuje playliste. !load <nazwa_zapisu>"""
        if not os.path.exists("music/"+name) or '.' in name:
            await ctx.send('Zapis nie istnieje')
            return
        with open("music/"+name,'r') as file:
            out = file.read().split(';')
        corr = 0
        err = 0
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        for i in out:
            url = 'https://www.youtube.com/watch?v='+i if not 'http' in i else i
            try:
                results = await player.node.get_tracks(url)
                if not results or not results['tracks']:
                    err+=1
                    continue
                track = results['tracks'][0]
                track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
                player.add(requester=ctx.author.id, track=track)
                corr+=1
            except:
                err+=1
        embed = discord.Embed(color=discord.Color.blurple())
        embed.title = 'Wczytano '+name
        embed.add_field(name='Udane: ',value =str(corr))
        embed.add_field(name='Błędy: ',value =str(err))
        await ctx.send(embed=embed)

        

    @commands.guild_only()
    @commands.command(aliases=['n'])
    async def np(self, ctx):
        """Wyświetla obecnie odtwarzany utwór. !np"""
        embed = discord.Embed(color=discord.Color.blurple())
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed.title = 'NP'
        track = player.current
        url = 'https://www.youtube.com/watch?v='+track["identifier"] if not 'http' in track["identifier"] else track["identifier"]
        embed.description = f'[{track["title"]}]({url})'
        embed.set_footer(text=str(self.bot.get_user(track.requester)))
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(aliases=['rm'])
    async def remove(self,ctx,pos):
        '''Usuwa utwór na danej pozycji, wymaga potwierdzenia przycieskiem USUŃ. !remove <pozycja>'''
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        pos = len(player.queue)-1 if pos=='last' else int(pos)-1
        tr = player.queue[pos]
        embed = discord.Embed(color=discord.Color.red())
        embed.title = 'Usunąć?'
        url = 'https://www.youtube.com/watch?v='+tr["identifier"] if not 'http' in tr["identifier"] else tr["identifier"]
        embed.description = f'[{tr["title"]}]({url})'
        msg = await ctx.send(embed=embed,
        components = [[
            Button(label = "Usuń", custom_id = "DEL", style=4)
        ]])
        try:
            interaction = await self.bot.wait_for("button_click",timeout=5, check = lambda i: i.custom_id == "DEL")
            embed = discord.Embed(color=discord.Color.red())
            embed.title = 'Usunięto'
            url = 'https://www.youtube.com/watch?v='+tr["identifier"] if not 'http' in tr["identifier"] else tr["identifier"]
            embed.description = f'[{tr["title"]}]({url})'
            await player.remove(pos)
            await interaction.edit_origin(embed=embed,
            components = [])
            if pos == 0:
                await player.play()
        except asyncio.TimeoutError:
            embed = discord.Embed(color=discord.Color.red())
            embed.title = 'Przedawniono'
            await msg.edit(embed=embed, components = [])

    @commands.guild_only()
    @commands.command(allsias=['cl'])
    async def clear(self,ctx):
        '''Usuwa wszytskie utwory z kolejki, wymaga potwierdzenia przycieskiem WYCZYŚĆ. !clear'''
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.red())
        embed.title = 'Czy chcesz wyczyścić całą playlistę?'
        msg = await ctx.send(embed=embed,
        components = [[
            Button(label = "Wyczyść", custom_id = "CLER", style=4)
        ]])
        try:
            interaction = await self.bot.wait_for("button_click",timeout=5, check = lambda i: i.custom_id == "CLER")
            embed = discord.Embed(color=discord.Color.red())
            embed.title = 'Wyczyszczono'
            player.queue = []
            player.pos = 0
            await interaction.edit_origin(embed=embed,
            components = [])
        except asyncio.TimeoutError:
            embed = discord.Embed(color=discord.Color.red())
            embed.title = 'Przedawniono'
            await msg.edit(embed=embed, components = [])

    @commands.guild_only()
    @commands.command()
    async def loop(self, ctx):
        '''Włącza/wyłącza powtarzanie kolejki. !loop'''
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        player.set_repeat(not player.repeat)
        if player.repeat:
            await ctx.send('Powtarzanie włączone')
        else:
            await ctx.send('Powtarzanie wwłączone')

    @commands.guild_only()
    @commands.command(aliases=['jp'])
    async def jump(self, ctx, npos):
        '''Przewija do utworu na danej pozycji. !jump <pozycja>'''
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if npos.isnumeric() and int(npos)>0 and int(npos) <= len(player.queue):
            player.pos = int(npos)-1
            await player.play(special=True)
            embed = discord.Embed(color=discord.Color.blurple())
            embed.title = 'Przeskoczono do pozycji '+npos
            track = player.current
            url = 'https://www.youtube.com/watch?v='+track["identifier"] if not 'http' in track["identifier"] else track["identifier"]
            embed.description = f'[{track["title"]}]({url})'
            await ctx.send(embed=embed)
        elif npos=="last":
            player.pos = len(player.queue)-1
            await player.play(special=True)
            embed = discord.Embed(color=discord.Color.blurple())
            embed.title = 'Przeskoczono do pozycji '+str(len(player.queue)-1)
            track = player.current
            url = 'https://www.youtube.com/watch?v='+track["identifier"] if not 'http' in track["identifier"] else track["identifier"]
            embed.description = f'[{track["title"]}]({url})'
            await ctx.send(embed=embed)
        else:
            await ctx.send('Użycie: !jump <pozycja>')

    @commands.guild_only()
    @commands.command(aliases=['fsh','fshuffle'])
    async def forceshuffle(self, ctx):
        '''Jednorazowe przemieszanie playlisty. !fshuffle'''
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await player.shuffel()

    @commands.guild_only()
    @commands.command(aliases=['sh'])
    async def shuffle(self, ctx, *mode):
        '''Zmienia tryb przemieszania\n0:wyłączenie 1:przemieszanie na koniec 2:każdy utwór losowy. !shuffle [tryb]'''
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        mode = mode[0]
        if mode and mode.isnumeric() and int(mode)>= 0 and int(mode)<=3:
            player.set_shuffle(int(mode))
        else:
            player.set_shuffle((player.shuffle+1)%4)
        if player.shuffle==0:
            await ctx.send('Przemieszanie wyłączone')
        elif player.shuffle==1:
            if not player.repeat:
                await ctx.send('Przemieszanie włączone na tryb 1 (losuje raz)\n**Wymagany loop do poprawnego funkcjonowania**')
            else:
                await ctx.send('Przemieszanie włączone na tryb 1 (losuje raz)')
        elif player.shuffle==2:
            await ctx.send('Przemieszanie włączone na tryb 2 (każdy losowy)')
        else:
            await ctx.send('Przemieszanie włączone na tryb 3 (każdy losowy bez powtórek)')
            

    @commands.guild_only()
    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        """Wychodzi z kanału głosowego. !disconnect"""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            # We can't disconnect, if we're not connected.
            return await ctx.send('Nie połączono.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            # Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
            # may not disconnect the bot.
            return await ctx.send('Nie jesteś na kanale głosowym!')

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await ctx.guild.change_voice_state(channel=None)
        await ctx.send('*⃣ | Rozłączono.')

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.responded:
            return
        if interaction.message.content.startswith('```Strona'):
            player = self.bot.lavalink.player_manager.get(interaction.guild.id)
            pageid = int(interaction.message.content.split('Strona ')[1].split(':')[0])+int(interaction.custom_id)-2
            queuesend = '```Strona '+str(pageid+1)+':\n'
            for idx, val in enumerate(player.queue[pageid*10:pageid*10+10],start=pageid*10):
                if idx == player.pos:
                    queuesend += '    ⬐ current track\n' + str(idx+1)+') '+val['title'] + '\n    ⬑ current track\n'
                else:
                    queuesend += ' '+str(idx+1)+') '+val['title'] + '\n' if idx<9 else str(idx+1)+') '+val['title'] + '\n'
            if pageid<1:
                btn1lock = True
            else:
                btn1lock = False
            if (pageid+1)*10>=len(player.queue):
                btn2lock = True
            else:
                btn2lock = False
            if player.shuffle==0:
                shuff = 'Przemieszanie wyłączone'
            elif player.shuffle==1:
                shuff = 'Przemieszanie włączone (raz losowane)'
            elif player.shuffle==2:
                shuff = 'Przemieszanie włączone (każdy losowy)'
            elif player.shuffle==3:
                shuff = 'Przemieszanie włączone (bez powtórek)'
            else:
                shuff = 'co sie odwaliło wtf'
            lood = 'Zapętlanie włączone' if player.repeat else 'Zapętlanie wyłączone'
            await interaction.edit_origin(content=queuesend+'\n'+shuff+'\n'+lood+'```',
            components = [[
                Button(label = "Prev", custom_id = "0", style=1, disabled=btn1lock),
                Button(label = "Next", custom_id = "2", style=1, disabled=btn2lock)
            ]])
        
def setup(bot):
    bot.add_cog(Music(bot))
