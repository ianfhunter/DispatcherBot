import discord
import json
import re
import sys
sys.path.append("..")
from RoomGenerator.DungeonTracker import DungeonTracker
from RoomGenerator.AssetManager import PlayerIconManager
from DispatcherBot.DBQueries import PlayerDB, GameDB
from discord.ext import commands
import datetime as dt

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


async def DM(who, what):
    where = who.dm_channel
    if where is None:
        await who.create_dm()
        where = who.dm_channel
    await where.send(what)

playerDB = PlayerDB()
gameDB = GameDB()
PIM = PlayerIconManager()


def inDMs(who, channel):
    if who.dm_channel == channel:
        return True
    return False


def areInGame(channel):
    if channel.id not in game_settings:
        return False
    return True

async def showRoom(channel):
    game = gameDB.get(channel.id)
    dungeon = game["dungeon"]

    for pID in game["players"]:
        p_obj = playerDB.get(pID)
        dungeon.add_player(pID, p_obj["icon"])

    room_img = dungeon.draw()
    await channel.send(file=discord.File(room_img))
    room_description = dungeon.describe()
    dungeon.debug()
    await channel.send(f"You enter the room. \n {room_description}")
    

async def connect_player(player, channel):
    pID = str(player)
    cID = str(channel.id)

    if not inDMs(player, channel):
        print("PC")
        # Start New Game
        game = gameDB.get(cID)
        if game is None:
            # Create new game
            await channel.send("Session opened")
            d = DungeonTracker()
            gameDB.save(cID, d, [], None, None)
            game = gameDB.get(cID)
        else:
            d = gameDB.get(cID)["dungeon"]

        assert(game is not None)

        players = game["players"]
        if players is None:
            players = set([])
        else:
            players = set(players)

        players.add(pID)
        players = list(players)
        gameDB.save(cID, d, players, None, None)

    # Create Player Entry if it doesn't exist
    player_entry = playerDB.get(pID)
    if player_entry is None:
        playerDB.save(pID, -1)

    if not inDMs(player, channel):
        await channel.send(
            f"""Welcome to the game {pID}."""
        )
    return True

@client.event
async def on_message(message):
    global game_settings

    print(">", message.content)
    if message.author == client.user:
        return

    if message.content.startswith('$choose'):
        await connect_player(message.author, message.channel)

        player = playerDB.get(message.author)
        choice = PIM.parseChoice(message.content)
        playerDB.save(message.author, int(choice))
        
        await DM(message.author, "Icon Changed.")
        # await message.channel.send("Icon Changed.")
            
    if message.content.startswith('$reset'):
        await message.channel.send("Resetting DBs.")
        playerDB.reset()
        gameDB.reset()

    if message.content.startswith('$open'):
        # TODO: Check if in combat
        game = gameDB.get(message.channel.id)
        if game is not None and game["start_time"] is not None:
            dungeon = game["dungeon"]
            dungeon.nextRoom() 
            await showRoom(message.channel)

    if message.content.startswith('$show'):
        # TODO: Check if in combat
        game = gameDB.get(message.channel.id)
        if game is not None and game["start_time"] is not None:
            await showRoom(message.channel)

    if message.content.startswith('$move'):
        # TODO: Check if in combat
        game = gameDB.get(message.channel.id)
        if game is not None and game["start_time"] is not None:
            dungeon = game["dungeon"]
            movement = message.content.split("$move")[1]
            print("movement", movement)
            status, msg = dungeon.movePlayer(message.author, movement)
            if status:
                await showRoom(message.channel)
            else:
                await message.channel.send(msg)

        

    if message.content.startswith('$join'):
        await connect_player(message.author, message.channel)

        player = playerDB.get(message.author)
        icon = player.get("icon", None)

        if icon == -1:
            await DM(message.author, 
                """
                Before adventuring, what would you like to represent your character?
                  use $choose <num> to pick from:
                  1) Fighter (default)
                  2) Archer
                  3) Mage
                  4) Cleric
                  5) Druid
                  6) Black Mage
                  7) Paladin
                """
        )

    if message.content.startswith('$start'):
        game = gameDB.get(message.channel.id)
        if game is not None:
            if game.get("start_time", None) is None :
                start = str(dt.datetime.now())
                gameDB.save(message.channel.id, game["dungeon"], game["players"], start, None)
                await showRoom(message.channel)
            else:
                await message.channel.send("A game is already in progress. You can cancel it with $end")
        else:
            await message.channel.send("No players in-game.")

    if message.content.startswith('$end'):
        game = gameDB.get(message.channel.id)
        if game is not None:
            end = str(dt.datetime.now())
            gameDB.save(message.channel.id, game["dungeon"], game["players"], game["start_time"], end)
            # TODO: Delete after 24hrs (Free) 
            await message.channel.send('The session is over. Hope you had fun!')
        else:
            await message.channel.send("No game in progress.")


    if message.content.startswith('$spawn'):
        # TODO: Check if in combat
        game = gameDB.get(message.channel.id)
        if game is not None and game["start_time"] is not None:
            dungeon = game["dungeon"]
            dungeon.spawnMonster(message.author)
            await showRoom(message.channel) 


settings = json.load(open("discord_settings.json"))
client_token = settings["client"]
bot_token = settings["bot_token"]
permission_int = 335932498

print(f"Invite Link: https://discordapp.com/oauth2/authorize?client_id={client_token}&scope=bot&permissions={permission_int}")

client.run(bot_token)

