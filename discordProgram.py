

import discord
import time
from discord.ext import commands, tasks
from botSecrets import discordSecrets
import asyncio
import random

# For implementing scheduler.
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

intent = discord.Intents.default()
intent.members = True
intent.messages = True
intent.reactions = True
intent.message_content = True
intent.guilds = True


# Might need an external database to hold the information
# of the patrol routes in the case that the bot goes offline.

# That way data doesn't reset with each startup.

client = commands.Bot(command_prefix='~', intents=intent)

botClientUser = discord.ClientUser(state=discord.Client, data={"username":"Worm Police", "id":discordSecrets["botId"],"discriminator":"7383", "bot": True, "avatar":"StringWurm.png"})
# List of servers the bot is in, with associated text channels to post in.
# Associated text channels will note if bot made them or if 
global patrol_route
global worm_channel
global server_list
global scheduler

scheduler = AsyncIOScheduler()

patrol_route = []
server_list = []

testing = True

# List of bot messages

WORM_WELCOME_DM_MSG = """
Hi. 

The Worm Police has gained jurisdiction within your server. 

Set the channel for worm checking with: `~set_worm_channel` Run this inside of the desired channel.
Define who's already on the watchlist with: `~define_worm_role [role-name]`

For a reminder, just do ~help_remind

Thanks for making your server a safer community. :worm:

*Non-implemented*

Designate a time for when to patrol the channel with: `~add_checking_time ##h##m` 
Designate a random patrol pattern with: `~add_checking_time random
Designate a patrol frequency: `~patrol_frequency [frequency per day]`

"""
WORM_CHANNEL_SET_MSG = "Thanks <@{0}>. We'll be patrolling <#{1}> now."
WORM_ROLE_SET_MSG = "Thanks <@{0}>. We'll keep an eye out on <@&{1}>."

# Finds the server in the list of patrol routes.
# Returns an empty string if the server can't be found.
def findRoute(guild):
    for route in patrol_route:
        if(route["server"] == guild):
            return route
    return ""

# Needs testing long term (need to wait or change job schedule temp)
async def assign_random_time():
    for route in patrol_route:
        print("Assigning random time for {}".format(route["server"].name))
        if(route["time"]["randomly_set"]):
            if(len(route["time"]["checking_time_ids"]) > 0):
                scheduler.remove_job(route["time"]["checking_time_ids"][0])
                route["time"]["checking_time_ids"].pop()
                route["time"]["checking_time"].pop()

            hours = random.randint(0, 23)
            minute = random.randint(0, 59)

            guild_job_id = str(route["server"].id)+"0"

            route["time"]["checking_time"].append("{0}h{1}m".format(hours, minute))
            route["time"]["checking_time_ids"].append(guild_job_id)

            def jobfunc():
                itsWormTime(route)

            scheduler.add_job(jobfunc, trigger=CronTrigger(hour=hours, minute=minute), id=guild_job_id)
            print("Post-job assignment")

# Mostly finished
# Needs message to send for setting time.  
@client.command()
async def add_checking_time(ctx, *args):
    settingGuild = findRoute(ctx.guild)

    if(args[0] == "random"):
        if(settingGuild["time"]["checking_time"] > 0):
            for id in settingGuild["time"]["checking_time_ids"]:
                scheduler.remove_job(id)

        settingGuild["time"] = {"randomly_set":True,
                                "checking_time":[], 
                                "checking_time_ids":[]}
        print(settingGuild)
    else:
        new_job_id = str(settingGuild["server"].id)+str(len(settingGuild["time"]["checking_time_ids"]))
        
        hoursandmins = args[0].split("h")
        hoursandmins = [hoursandmins[0], hoursandmins[1].split("m")[0]]

        settingGuild["time"]["checking_time"].append(args[0])
        settingGuild["time"]["checking_time_ids"].append(new_job_id)

        def jobfunc():
            itsWormTime(settingGuild)
            
        scheduler.add_job(jobfunc, trigger=CronTrigger(hour=hoursandmins[0], minute=hoursandmins[1]), id=new_job_id)

        if(settingGuild["time"]["randomly_set"]):
            settingGuild["time"]["randomly_set"] = False
        
        print(settingGuild)
        
# Mostly working. Add in messages to send to server.
@client.command()
async def remove_checking_time(ctx, *args):
    settingGuild = findRoute(ctx.guild)
    if args[0] in settingGuild["time"]["checking_time"]:
        popIndex = settingGuild["time"]["checking_time"].index(args[0])
        idToRemove = settingGuild["time"]["checking_time_ids"][popIndex]
        
        scheduler.remove_job(idToRemove)
        settingGuild["time"]["checking_time"].remove(args[0])
        settingGuild["time"]["checking_time_ids"].remove(idToRemove)

        if(len(settingGuild["time"]["checking_time"]) == 0):
            settingGuild["time"]["randomly_set"] = True
    
    print(settingGuild)
    
# Format server message
# Also add behavior to not show patrol time if random is true.
@client.command()
async def show_patrol_times(ctx):
    for time in findRoute(ctx.guild)["time"]["checking_time"]:
       await ctx.channel.send(time)

# Finished
# IDEA: Allow different role groups to have different times
# for worm checking. Have multiple worm groups.
@client.command()
async def define_worm_role(ctx, *args):
    # For testing:
    # await ctx.channel.send("DWR")
    # print("DWR")

    new_role_str = args[0] if len(args) > 0 else ""
    new_role = ""

    for role in findRoute(ctx.guild)["server"].roles:
        if role.name.lower() == new_role_str.lower():
            new_role = role
    
    if(new_role == ""):
        new_role = ctx.guild.default_role
        await ctx.channel.send("Sorry, the role '{}' doesn't exist. We're gonna watch everyone for now.".format(new_role_str))
        findRoute(ctx.guild)["wormer_role"] = new_role
    elif(new_role == findRoute(ctx.guild)["wormer_role"]):
        await ctx.channel.send("This role is already being watched.")
    else:
        findRoute(ctx.guild)["wormer_role"] = new_role
        await ctx.channel.send(WORM_ROLE_SET_MSG.format(ctx.author.id, findRoute(ctx.guild)["wormer_role"].id))
    # print("role: {}".format(findRoute(ctx.guild)["wormer_role"]))

# Finished
@client.command()
async def set_worm_channel(ctx, *args):
    # For testing:
    # await ctx.channel.send("SWC")
    # print("SWC")
    new_channel = ctx.channel

    findRoute(ctx.guild)["worm_chat"] = new_channel
    # print("channel: {}".format(findRoute(ctx.guild)["worm_chat"]))

    await ctx.channel.send(WORM_CHANNEL_SET_MSG.format(ctx.author.id,new_channel.id))

    print(findRoute(ctx.guild)["worm_chat"])

# For manually sending a test message
@client.command()
async def test_send(ctx):
    await itsWormTime(findRoute(ctx.guild))

# Finished. 
@client.command()
async def help_remind(ctx):
    print("Help recieved")
    await ctx.author.send(content=WORM_WELCOME_DM_MSG)

@client.event
async def on_guild_join(guild):
    global server_list
    global patrol_route

    server_list.append(guild)
    route_info = {"server":guild, 
                  "wormer_role":"", 
                  "worm_chat":"", 
                  "time":{
                      "randomly_set":True, 
                      "checking_time":[], 
                      "checking_time_ids":[]
                      }
                      }
    patrol_route.append(route_info)
    guild.owner.send()

@client.event
async def on_guild_leave(guild):
    global server_list
    global patrol_route

    server_list.remove(guild)
    for route in patrol_route:
        if(route["server"] == guild):
            patrol_route.remove(route)
            return

# Decide at a random time on the hour/hours or 
# set time to send message.
# Add in scheduler as shown here:
# https://stackoverflow.com/questions/64491012/how-do-i-send-a-message-in-a-channal-at-a-specific-time
@client.event
async def on_ready():
    global patrol_route
    global server_list

    # Sanity check of sorts
    for guild in client.guilds:
        if(findRoute(guild) == ""):
            server_list.append(guild)
            patrol_route.append(
                {"server": guild, 
                 "wormer_role":"", 
                 "worm_chat":"",
                 "time":{
                     "randomly_set":True, 
                     "checking_time":[], 
                     "checking_time_ids":[]
                     }
                })
    
    #vvvvv This is all for testing the send message vvvvv

    # Thought: Pivot from a new channel every time to
    # threads that open and then close after a set
    # time
    # route = patrol_route[0]
    # guild = route["server"]

    # Make in defineTime, when added to server, 
    # make default worm schedule time to 
    # either midnight or 6pm

    # For testing purposes
    for route in patrol_route:
        await itsWormTime(route)

    for job in scheduler.get_jobs():
        if job.id is not "random-time-assigner":
            scheduler.add_job(assign_random_time, trigger=CronTrigger(hour="00"), id="random-time-assigner")

    scheduler.start()
   

# Replace with creating thread, and then closing thread after like 30 minutes or an hour.
    #await worm_channel.delete()

@client.event
async def on_disconnect():
    if testing:
        await worm_channel.delete()

# Creates a thread for wormers to reply in, and closes after a designated time.
async def itsWormTime(server):
    # Who up?
    theImage = discord.File("IMG_3297.JPG")
    
    print(server) 
    global patrol_route
    worm_channel = ""
    worm_role = ""

    # Set wormer role
    if(server["wormer_role"] == ""):
        worm_role = server["server"].default_role
        server["wormer_role"] = worm_role
    else:
        worm_role = server["wormer_role"]

    # Set channel role
    if(server["worm_chat"] == ""):
        worm_channel = await server["server"].create_text_channel("worm-check", overwrites={server["server"].default_role: discord.PermissionOverwrite(read_messages=False),
    server["server"].me: discord.PermissionOverwrite(read_messages=True)})
        
        await worm_channel.set_permissions(worm_role, read_messages = True, send_messages=True)
        
        server["worm_chat"] = worm_channel
    else:
        worm_channel = server["worm_chat"]

    # This can probably be moved into the whole
    # thread creating message send function.
    worm_gang = []
    memberList = client.get_all_members()
    for member in memberList:
        # member_role_list = []
        # for role in member.roles:
        #     member_role_list.append(role.name)
        if(worm_role in member.roles):
            worm_gang.append(member)
    # print(worm_gang)
    # Change to create a thread to send message.
    wormingThread = await worm_channel.create_thread(name="Who up playing with they worm?", type=discord.ChannelType.public_thread, auto_archive_duration=60)
    await wormingThread.send(content="", file=theImage)

    # # Close thread after 60 seconds
    # closeTime = time.time() + 60

    # while(time.time() != closeTime):
    #     wormingThread.locked = False

    #newThread = worm_channel.create_thread()
    #await worm_channel.send(content="", file=theImage)

def runDiscord():
    print("Running Discord!")
    client.run(discordSecrets["botToken"])
