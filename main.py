import discord
import json
import re
import sys
sys.path.append("..")
from RoomGenerator.main import RoomFactory, Cell

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

player_settings = {
    
}

game_settings = {
    
}

@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return

    if message.content.startswith('$choose'):
        get_choice = re.search(r'\d+', message.content).group()
        if get_choice is not None:
            print("Choice:", get_choice)

            choices = {
                "1": Cell.Type.PLAYER_FIGHTER,
                "2": Cell.Type.PLAYER_ARCHER,
                "3": Cell.Type.PLAYER_MAGE,
                "4": Cell.Type.PLAYER_CLERIC,
                "5": Cell.Type.PLAYER_DRUID,
                "6": Cell.Type.PLAYER_BMAGE,
                "7": Cell.Type.PLAYER_PALADIN
            }
            character = choices[str(get_choice)]
            room = game_settings[message.channel.id]["room"]
            rf = game_settings[message.channel.id]["room_factory"]
            rf.insert_thing(room, character)
            room_img = room.show(gui="img")
            await message.channel.send("Good choice. You have entered the game")
            
            # await message.channel.send(file=discord.File(room_img))
            


    if message.content.startswith('$open'):
        # TODO: Check if in combat
        pass

    if message.content.startswith('$join'):

        if message.channel.id not in game_settings:
            await message.channel.send("Session opened")
            rf = RoomFactory()
            r = rf.create_room()
            game_settings[message.channel.id] = {}
            game_settings[message.channel.id]["room_factory"] = rf
            game_settings[message.channel.id]["room"] = r
            game_settings[message.channel.id]["started"]= False


        await message.channel.send(
            f"""Welcome to the game {message.author}."""
        )   
        if message.author not in player_settings:
            await message.channel.send("""
                Before we can add you, what would you like to represent your character?
                  use $choose <num> to pick from:
                  1) Fighter
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
                r = game_settings[message.channel.id]["room"]
                room_img = r.show(gui="img")
                await message.channel.send(file=discord.File(room_img))
                room_description = r.show(gui="describe")
                game_settings[message.channel.id]["started"] = True
                await message.channel.send(f"You enter the room. \n {room_description}")
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
