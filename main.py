import discord
import json
import re
import sys
sys.path.append("..")
from RoomGenerator.DungeonTracker import DungeonTracker

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

player_settings = {
    
}

game_settings = {
    
}

def areInGame(channel):
    if channel.id not in game_settings:
        return False
    return True

async def showRoom(channel):
    dungeon = game_settings[channel.id]["dungeon"]
    room_img = dungeon.draw()
    await channel.send(file=discord.File(room_img))
    room_description = dungeon.describe()
    game_settings[channel.id]["started"] = True
    await channel.send(f"You enter the room. \n {room_description}")


async def connect_player(player, channel):
    
    if channel.id not in game_settings:
        await channel.send("Session opened")

        game_settings[channel.id] = {}
        game_settings[channel.id]["started"]= False
        d = DungeonTracker()
        game_settings[channel.id]["dungeon"] = d

    d = game_settings[channel.id]["dungeon"]
    d.add_player(player)

    await channel.send(
        f"""Welcome to the game {player}."""
    )
    return True

@client.event
async def on_message(message):
    global game_settings

    print(message.content)
    if message.author == client.user:
        return

    if message.content.startswith('$choose'):
        await connect_player(message.author, message.channel)

        choice = re.search(r'\d+', message.content).group()
        if choice is not None:
            print("Choice:", choice)
            dungeon = game_settings[message.channel.id]["dungeon"]
            player = dungeon.get_player(message.author)
            player.choose_icon(choice)
            await message.channel.send("Good choice. Icon Changed")
            
    if message.content.startswith('$open'):
        # TODO: Check if in combat
        if areInGame(message.channel):
            dungeon = game_settings[message.channel.id]["dungeon"]
            dungeon.nextRoom()
            await showRoom(message.channel)
        

    if message.content.startswith('$join'):
        await connect_player(message.author, message.channel)

        if message.author not in player_settings:
            await message.channel.send("""
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
        if message.channel.id in game_settings:
            if not game_settings[message.channel.id]["started"]:
                await showRoom(message.channel)
            else:
                await message.channel.send("A game is already in progress. You can cancel it with $end")


    if message.content.startswith('$end'):
        if message.channel.id in game_settings:
            game_settings.pop(message.channel.id)
            await message.channel.send('The session is over. Hope you had fun!')
        else:
            await message.channel.send("No game in progress.")


settings = json.load(open("discord_settings.json"))
client_token = settings["client"]
bot_token = settings["bot_token"]
client.run(bot_token)

print("Invite Link: https://discordapp.com/oauth2/authorize?client_id={client_token}&scope=bot&permissions=0")
