import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

ALLOWED_USERS = {
    104808415020261376  # replace with your actual Discord ID
}

# Discord permissions/intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# Event: bot started
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Simple test command
@bot.command()
async def ping(ctx):

    if ctx.author.id not in ALLOWED_USERS:
        await ctx.send("Unauthorized.")
        return

    await ctx.send("pong")

# Run bot
bot.run(TOKEN)