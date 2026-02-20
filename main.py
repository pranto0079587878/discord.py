import discord
from discord.ext import commands
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")  # Render-এ variable দিয়ে নেবে, এখানে hardcode করো না!

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True

bot = commands.Bot(command_prefix='!', intents=intents)

message_history = {}

MAX_MESSAGES = 5
TIME_WINDOW = 10
MAX_MENTIONS = 5

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} | Security Bot Ready!')

@bot.event
async def on_message(message):
    if message.author.bot or message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return

    now = message.created_at.timestamp()
    user_id = message.author.id

    if user_id not in message_history:
        message_history[user_id] = []

    message_history[user_id] = [t for t in message_history[user_id] if now - t < TIME_WINDOW]
    message_history[user_id].append(now)

    if len(message_history[user_id]) > MAX_MESSAGES:
        await message.delete()
        await message.author.timeout(timedelta(minutes=10), reason="Flood/Spam detected")
        await message.channel.send(f"{message.author.mention} Stop spamming! (too fast messages)", delete_after=10)
        return

    mentions_count = len(message.mentions) + (1 if message.mention_everyone or message.mention_roles else 0)
    if mentions_count >= MAX_MENTIONS:
        await message.delete()
        await message.author.timeout(timedelta(minutes=10), reason="Mass mention detected")
        await message.channel.send(f"{message.author.mention} No mass pings! ({mentions_count} mentions)", delete_after=10)
        return

    await bot.process_commands(message)

bot.run(TOKEN)
