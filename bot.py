import os
import asyncio
import discord
import requests

from dotenv import load_dotenv
from discord.ext import commands, tasks

from logs import logger
from modules.database import add_player, delete_player, update_queues, get_message, show_player, UniqueViolation
from modules.show import command_info, Commands

load_dotenv()

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
DISCORD_CHANNEL_ID = os.environ['DISCORD_CHANNEL_ID']
RIOT_TOKEN = os.environ['RIOT_TOKEN']

intents = discord.Intents.default()
intents.message_content =True

bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(hours=4)
async def query_advance():
    channel = bot.get_channel(int(DISCORD_CHANNEL_ID))
    if channel:
        updates = update_queues(RIOT_TOKEN)
        if updates and len(updates)>0:
            for update in updates:
                message_content = (
                    f"**{update['name']}** has been challenging the Rift!\n"
                    f"This summoner {"got to" if update['up'] else "fell to"} **{update['tier']} {update['rank']}**.\n"
                    f"{get_message(update['up'])}"
                )
                await channel.send(message_content)

@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} has come from the Summoner's Rift.")
    if not query_advance.is_running():
        query_advance.start()

@bot.command()
async def lolBotStatus(ctx):
    await ctx.send("Online! Just daydreaming about T1's tripeat.")

@bot.command()
async def joinParty(ctx, *, message):
    logger.info(f'Adding {message} to the database.')
    gameName = message.split("#")[0]
    tagLine = message.split("#")[1]

    headers = {
        "X-Riot-Token":RIOT_TOKEN
    }

    response = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}",headers=headers)
    player_info = response.json()
    puuid = player_info['puuid']

    response = requests.get(f"https://la1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}",headers=headers)
    queue_info = response.json()

    flex_data = list(filter(lambda x : 'RANKED_FLEX_SR' in x['queueType'],queue_info))[0]
    solo_data = list(filter(lambda x : 'RANKED_SOLO_5x5' in x['queueType'],queue_info))[0]

    add_player(
        puuid,
        flex_data['tier'],
        flex_data['rank'],
        flex_data['leaguePoints'],
        solo_data['tier'],
        solo_data['rank'],
        solo_data['leaguePoints']
    )

    try:
        if response.status_code == requests.codes.ok:
            logger.info(f"Added {gameName} to the database.")
            await ctx.channel.send(f"{player_info['gameName']} #{player_info['tagLine']} added to the party!")
        else:
            await ctx.channel.send("Something went wrong with Rito. :(")
            logger.error(f'Error with the Riot API: {response.status_code}')
    except UniqueViolation as e:
        logger.error(f'{message} already in the server.')
        await ctx.channel.send(f"It seems {gameName} is already at the party.")
    except Exception as e:
        logger.error(f"Unknown issue: {e.__class__}")
        await ctx.channel.send("I wasn't built right...")

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

@bot.command()
async def showPlayer(ctx, *, message):
    try:
        playerName, tagLine = message.split('#')
        try:
            player = show_player(playerName, tagLine, RIOT_TOKEN)
            await ctx.channel.send(
                f'**{playerName}#{tagLine}** \n'
                f'Flex: **{player[0]} {player[1]}** ({player[2]}LP)\n'
                f'Solo: **{player[3]} {player[4]}** ({player[5]}LP)'
            )
        except Exception as error:
            logger.error(f"Error pulling data from the database: {error.__class__}")
            await ctx.channel.send("Couldn't get the player data, has it been registered?")
    except:
        logger.error(f"Error parsing the player name from the message: {message}")
        await ctx.channel.send('Something is wrong with that player name.')

@bot.command()
async def deletePlayer(ctx, *, message):
    try:
        playerName, tagLine = message.split('#')
        deleted = delete_player(playerName, tagLine, RIOT_TOKEN)
        if deleted:
            logger.info(f"{playerName} deleted from database.")
            await ctx.channel.send(f'Sad to see you go {playerName}.\n You can always come back using the _joinParty_ command!')
    except (ValueError, IndexError):
        ctx.channel.send('Something is wrong with that player name')
    except Exception as e:
        logger.error(f"Error deleting {playerName} from database: {e.__class__}")
        await ctx.channel.send("There was an error deleting the player, please try later.")

bot.run(DISCORD_TOKEN)
