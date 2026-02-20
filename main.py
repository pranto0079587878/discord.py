import discord
from discord.ext import commands
from datetime import timedelta
import os
from dotenv import load_dotenv
import threading
from flask import Flask

load_dotenv()

TOKEN = os.getenv("TOKEN")

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

# Dummy Flask web server to keep Render happy
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_app():
    port = int(os.environ.get('PORT', 8080))  # Render sets PORT
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Start Flask in a thread
threading.Thread(target=run_app).start()

bot.run(TOKEN)
