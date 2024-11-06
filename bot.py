import discord
import threading
import time
import random
from discord.ext import commands, tasks
from discord.errors import Forbidden
import datafunctions as data
import csv

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='@', intents=intents)

whitelisted_users = range(1,12)
tipCooldown = False
hell = False    
pingCount = 0
active_channel = None
ctxClass = None
enableDM = False

with open('targetUser.txt', 'r') as file:
    targetUser = file.read()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Start the periodic task when the bot is ready
    hell_loop.start()

@bot.event
async def on_message(message):
    global hell
    global targetUser
    global pingCount
    global tipCooldown
    global whitelisted_users
    global active_channel
    
    # Avoid the bot responding to itself
    if message.author == bot.user:
        return
    
    print(f"{message.author} said {message.content}")

    # Check if the bot should respond to all messages
    if hell:
        if pingCheck(message.content):
            if "OVERRIDE" in message.content:
                await retarget(message)
            if int(data.read_row('userid', str(extract_user_id(targetUser)))['id']) in whitelisted_users: # check if target in whitelist
                if data.read_row('username', str(message.author))['userid'] == extract_user_id(targetUser): # if pinger is the target
                    await retarget(message)
                else:
                    if message.channel.id == active_channel:
                        await message.channel.send(f"You can't pass the ping {data.read_row('username', str(message.author))['nickname']}.")
            else: # if target is not in whitelist
                await retarget(message)
        else:
            if not tipCooldown:
                if message.channel.id == active_channel:
                    await message.channel.send(f'TIP: If you\'re being targeted, you can ping someone else to pass the pings to them')
                    tipCooldown = True
                    threading.Thread(target=tipcd).start()

    # Process commands if present
    await bot.process_commands(message)

async def retarget(message):
    global pingCount
    global targetUser
    if "OVERRIDE" in message.content:
        message.content = message.content.replace("OVERRIDE", "")
    await message.channel.send(f'New Target: {message.content}')
    targetUser = message.content
    
    with open('targetUser.txt', 'w') as file:
        file.write(targetUser)
    pingCount = 0
    if not data.userid_exists(extract_user_id(targetUser)):
        the_userid = extract_user_id(message.content)
        username = await get_username_from_id(the_userid)
        data.add_row({
            'id': str(data.get_next_id() + 1),
            'username': str(username),
            'nickname': str(username),
            'userid': str(the_userid),
            'totalpingcount': 0
        })

@bot.command()
async def begin(ctx):
    global ctxClass
    global hell
    global active_channel
    hell = True
    ctxClass = ctx
    active_channel = ctx.channel.id
    await ctx.send(f'Starting.')

@bot.command()
async def stop(ctx):
    global hell
    hell = False
    await ctx.send(f'Stopped.')
    
@bot.command()
async def toggleDM(ctx):
    global enableDM
    enableDM = not enableDM
    await ctx.send(f'Toggled to {enableDM}')

@bot.command()
async def leaderboards(ctx):
    with open('userdata.csv', 'r') as file:
        reader = csv.DictReader(file)
        extracted_data = list(reader)  # Read all rows into a list

    guild_id = str(ctx.guild.id)  # Get the guild ID
    guild_member_ids = [str(member.id) for member in ctx.guild.members]

    # Filter users based on the user_id and handle missing 'user_id' key
    filtered_data = [data for data in extracted_data if data.get('userid') and str(data['userid']) in guild_member_ids]

    sorted_data = sorted(filtered_data, key=lambda x: int(x["totalpingcount"]), reverse=True)

    string = '# Total Ping Count Leaderboards:\n'
    for index in range(len(sorted_data)):
        if index == 0:
            string += f"**"
        string += f"{index+1}) {sorted_data[index]['nickname']} — {sorted_data[index]['totalpingcount']}\n"
        if index == 0:
            string += f"**"

    await ctx.send(f"{string}")

@tasks.loop(seconds=2)  # Run this task every second
async def hell_loop():
    global enableDM
    global hell
    global targetUser
    global pingCount
    global channel
    global ctxClass
    if hell:
        pingCount = pingCount + 1
        row = data.read_row('userid', str(extract_user_id(targetUser)))
        row['totalpingcount'] = str(int(row['totalpingcount']) + 1)
        data.save_row(row)
        channel = bot.get_channel(active_channel)
        await channel.send(f'{targetUser} x{pingCount} ({row['totalpingcount']})')
        userID = int(extract_user_id(targetUser))
        if ctxClass:
            memberDM = ctxClass.guild.get_member(userID)
        if memberDM and enableDM:
            try:
                await memberDM.send(f'{targetUser} x{pingCount} ({row['totalpingcount']})')
            except Forbidden:
                print(f"Cannot send message to {targetUser}.")

def tipcd():
    global tipCooldown
    time.sleep(10)
    tipCooldown = False
    return

def pingCheck(message):
    openingBracket, closingBracket = -1, -1
    for character_index in range(len(message)):
        if message[character_index:(character_index+2)] == '<@':    openingBracket = character_index
        if message[character_index] == '>':                         closingBracket = character_index
    if openingBracket != -1 and closingBracket != -1:
        if all(char.isdigit() and 0 <= int(char) <= 9 for char in message[openingBracket+2:closingBracket]):
            return True
    return False

def extract_user_id(message):
    # Find the positions of '<@' and '>'
    opening_bracket = message.find('<@')
    closing_bracket = message.find('>', opening_bracket)
    
    # Check if both brackets were found and the format is correct
    if opening_bracket != -1 and closing_bracket != -1 and closing_bracket > opening_bracket:
        # Extract the substring containing the user ID
        user_id_str = message[opening_bracket + 2:closing_bracket]
        
        # Ensure the extracted part is a valid number
        if user_id_str.isdigit():
            return user_id_str
    
    # Return None if no valid user ID is found
    return None

async def get_username_from_id(user_id):
    try:
        user = await bot.fetch_user(user_id)
        return user.name
    except discord.NotFound:
        return "User not found"
    except discord.HTTPException as e:
        print(f"HTTP Exception: {e}")
        return "Failed to fetch user"
    except Exception as e:
        print(f"Unexpected exception: {e}")
        return "Error"

with open('api_key.txt', 'r') as file:
    api_key = str(file.read())
# Run the bot with your token
bot.run(api_key)