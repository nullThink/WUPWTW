

import discord
import time
from discord.ext import commands, tasks
from botSecrets import discordSecrets

intent = discord.Intents.default()
intent.members = True
intent.messages = True

client = commands.Bot(command_prefix='$w', intents=intent)

WORM_GANG_ROLE = "Captain"
worm_gang = []
theImage = discord.File("IMG_3297.jpg")

# Of the form {name: "",
# leader: discordName+ID,
# members: []}
open_gangs = []

@client.event
async def on_ready():
    memberList = client.get_all_members()
    for member in memberList:
        print(member.name)
        for role in member.roles:
            if(role.name == WORM_GANG_ROLE):
                worm_gang.append(member)
        print(" ")
    
    for wormer in worm_gang:
       await wormer.send("",file=theImage)

# @client.command()
# async def joingang(ctx, *args):
#     ctx.add_role()

# @client.command()
# async def creategang(ctx, *args):
#     open_gangs.append()

# @client.command()
# async def showgangs(ctx, *args):
#     for gang in open_gangs:
#         ctx.send(gang)


def runDiscord():
    print("Running Discord!")
    client.run(discordSecrets["botToken"])
