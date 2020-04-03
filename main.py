import discord
import json

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$monster'):
        # await message.channel.send('Hello!')
        pass

settings = json.load(open("discord_settings.json"))
client_token = settings["client"]
bot_token = settings["bot_token"]
client.run(bot_token)

print("Invite Link: https://discordapp.com/oauth2/authorize?client_id={client_token}&scope=bot&permissions=0")
