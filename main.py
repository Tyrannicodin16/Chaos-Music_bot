import discord
from discord.ext import commands
from time import sleep
import requests
from pytube import YouTube
from moviepy.editor import AudioFileClip
from datetime import datetime
from os.path import dirname
from os import chdir
from sys import argv

chdir(dirname(argv[0]))

with open("info.txt", "r") as f:
    lines = f.readlines()
    fpath = "Path goes here"
    token = str(lines[1])

bot = commands.Bot(command_prefix="!", help_command=None)
queue_list = []
current = 0
guild_ids = [803197798639992853]

#HELP COMMAND#
@bot.command()
async def help(ctx):
    await ctx.send("Custom help command")
#HELP COMMAND END#

def embed(title, titleurl, description, fields, values, thumb):
    embed = discord.embeds.Embed()
    embed=discord.Embed(title=title, url=titleurl, description=description, color=0x0088ff)
    embed.set_author(name="Chaos Music", url="https://top.gg", icon_url="https://cdn.discordapp.com/avatars/798867117063405600/02b608005fd461c1c5c6eab72e2d30cb.png")
    embed.set_thumbnail(url=thumb)
    for field in fields:
        val = values[fields.index(field)]
        embed.add_field(name=field, value=val, inline=False)
    embed.set_footer(text="Chaos Music by Tyrannicodin16", icon_url="https://cdn.discordapp.com/avatars/547104418131083285/2ecad31df04d3db0d9b41be9f1f76b1b.png")
    embed.timestamp = datetime.today()
    return embed

def download(url, added):
    yt = YouTube(url=url)
    vid = yt.streams.filter(only_audio=True).first()
    vid.download(filename=added)
    return vid.title

def next(*self):
    global queue_list
    global current
    if queue_list and not len(queue_list) >= 10:
        if current > len(queue_list)-1:
            current = 0
        for client in bot.voice_clients:
            if client.is_playing():
                vol = client.source.volume
                client.stop()
                vnam = queue_list[current].songnae
                audio_source = discord.FFmpegPCMAudio(executable=fpath, source=vnam+".mp4")
                client.play(audio_source, after=next)
                client.source = discord.PCMVolumeTransformer(client.source, volume=vol)
            else:
                vnam = queue_list[current].songnae
                audio_source = discord.FFmpegPCMAudio(executable=fpath, source=vnam+".mp4")
                client.play(audio_source, after=next)
                client.source = discord.PCMVolumeTransformer(client.source, volume=0.5)
        current += 1

class song():
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.songnae = str(position)

#COMMANDS HERE#
@bot.command()
async def ping(ctx):
    await ctx.send(str(round(bot.latency*1000))+"ms")

@bot.command()
async def volume(ctx, volume):
    volume = int(volume)
    got = False
    if 0 <= volume <= 100:
        volume = volume / 100
    else:
        await ctx.send('Please enter a volume between 0 and 100')
    for client in bot.voice_clients:
        got = True
        client.source.volume = volume
    if not got:
        await ctx.send("Bot not connected")

@bot.command()
async def connect(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        client = await channel.connect()
        audio_source = discord.FFmpegPCMAudio(executable=fpath, source='init.mp3')
        client.play(audio_source, after=None)
    else:
        await ctx.send("You are not connected to a voice channel")

@bot.command()
async def play(ctx, search):
    global queue_list
    global current
    got = False
    for client in bot.voice_clients:
        if client.guild == ctx.guild:
            term = search.split(" ")
            string = "https://www.youtube.com/results?search_query="
            for item in term:
                string = string + item + "+"
            th = requests.get(string)
            r = th.text
            r = r.split("\"/watch?v=")
            r.pop(0)
            nr = []
            for bitty in r:
                nr.append(bitty.split("\"")[0])
            string = f"https://www.youtube.com/watch?v={nr[0]}"
            msg = await ctx.send("Downloading...")
            lesong = song(str(ctx.guild.name), len(queue_list))
            snam = download(string, lesong.songnae)
            lesong.name = snam
            queue_list.append(lesong)
            if len(queue_list) == 1:
                next()
                await msg.edit(content="Now playing: "+snam)
            else:
                await msg.edit(content="Now queued: "+snam)
            got = True
    if not got:
        await ctx.send("Bot not connected")
        

@bot.command()
async def disconnect(ctx):
    got = False
    for client in bot.voice_clients:
        if client.guild == ctx.guild:
            await client.disconnect()
            got = True
    if not got:
        await ctx.send("Bot not connected")

@bot.command()
async def skip(ctx):
    for client in bot.voice_clients:
        client.stop()

@bot.command()
async def queue(ctx, do):
    global queue_list
    global current
    if do == "clear":
        queue_list = []
        current = 0
    elif do == "show":
        values = []
        fields = []
        for song in queue_list:
            values.append(song.name)
            fields.append(str(song.position+1)+".")
        thumb = "https://github.com/Tyrannicodin16/Chaos-Music_bot/blob/main/queuicon.png?raw=true"
        invite = "https://discord.com/api/oauth2/authorize?client_id=798867117063405600&permissions=7669840&scope=bot"
        embeder = embed("Queue", invite, "This is the current queue!", fields, values, thumb)
        await ctx.send(embed=embeder)
    else:
        await ctx.send("That is not a valid argument")

@bot.command()
async def pause(ctx):
    got = False
    for client in bot.voice_clients:
        client.pause()
        got = True
    if not got:
        await ctx.send("Bot not connected")

@bot.command()
async def resume(ctx):
    got = False
    for client in bot.voice_clients:
        client.resume()
        got = True
    if not got:
        await ctx.send("Bot not connected")
#COMMANDS END#

#LISTENERS HERE#

#LISTENERS END#

bot.run(token)
