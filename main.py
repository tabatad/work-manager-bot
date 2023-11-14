import discord
from discord.ext import commands, tasks

import os
from dotenv import load_dotenv
from datetime import time, timezone, timedelta, datetime

# Time formatting
def get_time_str(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return str(h) + '時間' + str(m) + '分' + str(s) + '秒'

# Get user ID for each guild
def get_user_id_per_guild(user, guild):
    return str(user.id) + str(guild.id)

# Define bot
bot = commands.Bot(command_prefix="!",intents = discord.Intents.all())

# Init time dictionary
pretime_dict = {}
daily_dict = {}
total_dict = {}

# Set the tiem to run the batch prcess
JST = timezone(timedelta(hours=+9), "JST")
bat_time = time(hour=4, tzinfo=JST)

# Init daily_dict at regular time
@tasks.loop(time=bat_time)
async def bat_task():
    global daily_dict
    daily_dict = {}

# Start listen
@bot.event
async def on_ready():
    print("ready")

    bat_task.start()

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(exec)

# Post work hours to the '作業ログ' channel when exiting the voice channel
@bot.event
async def on_voice_state_update(member, before, after):
    if(before.channel is None):
        pretime_dict[member.id] = datetime.now()
    elif(after.channel is None):
        duration_time = pretime_dict[member.id] - datetime.now()
        duration_time_fixed = int(duration_time.total_seconds()) * -1
        duration_time_str = get_time_str(duration_time_fixed)

        guild = before.channel.guild
        id = get_user_id_per_guild(member, guild)

        if(id in total_dict):
            total_dict[id] += duration_time_fixed
        else:
            total_dict[id] = duration_time_fixed

        if(id in daily_dict):
            daily_dict[id] += duration_time_fixed
        else:
            daily_dict[id] = duration_time_fixed
        
        embed = discord.Embed(
            title=member.name + "の作業時間",
            color=0x00ff00,
            description=duration_time_str
        )

        guild = before.channel.guild
        for channel in guild.text_channels:
            if(channel.name == '作業ログ'):
                await channel.send(embed=embed)

# Show daily working time
@bot.tree.command(name="daily", description="show daily working time")
async def daily(interaction: discord.Interaction):
    id = get_user_id_per_guild(interaction.user, interaction.guild)

    embed = None
    if(id in daily_dict):
        time = get_time_str(daily_dict[id])
        embed = discord.Embed(
            title=interaction.user.name + "の今日の作業時間",
            color=0xff0000,
            description=time
        )
    else:
        embed = discord.Embed(
            title=interaction.user.name + "の今日の作業時間",
            color=0xff0000,
            description="まだ作業をしていません"
        )
    await interaction.response.send_message(embed=embed)

# Show total working time
@bot.tree.command(name="total", description="show total working time")
async def total(interaction: discord.Interaction):
    id = get_user_id_per_guild(interaction.user, interaction.guild)

    embed = None
    if(id in total_dict):
        time = get_time_str(total_dict[id])
        embed = discord.Embed(
            title=interaction.user.name + "の累計作業時間",
            color=0x0000ff,
            description=time
        )
    else:
        embed = discord.Embed(
            title=interaction.user.name + "の累計作業時間",
            color=0x0000ff,
            description="まだ作業をしていません"
        )
    await interaction.response.send_message(embed=embed)

# Load bot token
load_dotenv()
bot.run(os.getenv("TOKEN"))
