import os
import discord
import logging
import requests

from dotenv import load_dotenv
from discord.ext import commands

from modules.database import add_player
from modules.show import command_info, Commands

load_dotenv()

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = os.environ['DISCORD_CHANNEL_ID']
RIOT_TOKEN = os.environ['RIOT_TOKEN']
RIOT_ROOT = os.environ['RIOT_URL_ROOT']

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content =True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} has come from the Summoner's Rift.")

@bot.command()
async def lolBotStatus(ctx):
    await ctx.send("Online! Just daydreaming T1's tripeat.")

@bot.command()
async def joinParty(ctx, *, message):
    gameName = message.split("#")[0]
    tagLine = message.split("#")[1]

    response = requests.get(f"{RIOT_ROOT}account/v1/accounts/by-riot-id/{gameName}/{tagLine}/?api_key={RIOT_TOKEN}")
    player_info = response.json()
    puuid = player_info['puuid']

    response = requests.get(f"https://la1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={RIOT_TOKEN}")
    queue_info = response.json()

    flex_data = list(filter(lambda x : 'RANKED_FLEX_SR' in x['queueType'],queue_info))[0]
    solo_data = list(filter(lambda x : 'RANKED_SOLO_5x5' in x['queueType'],queue_info))[0]

    print(flex_data,solo_data)

    add_player(puuid,flex_data['tier'],flex_data['rank'],solo_data['tier'],solo_data['rank'])

    try:
        if response.status_code == requests.codes.ok:
            await ctx.channel.send(f"{player_info['gameName']} #{player_info['tagLine']} added to the party!")
        else:
            await ctx.channel.send("Something went wrong with Rito. :(")
    except Exception as e:
        await ctx.channel.send("I wasn't built right...")
        raise e


@bot.command()
async def show(ctx, *, message):
    command = command_info(message)
    message_content = (
        f"**{'Not found' if command.value == "" else command.value}**\n"
        f"**Description:** {command.description}\n"
        f"**How to use:** {command.instructions}"
    )
    await ctx.channel.send(message_content)

@bot.command()
async def listCommands(ctx):
    message_content = "\n".join([f"**{command.value}:** {command.description}" for command in filter(lambda x : x.value!="",Commands)])
    await ctx.channel.send(message_content)

bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)