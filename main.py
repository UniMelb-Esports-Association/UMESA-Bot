"""The entry point of the program which configures and runs the bot."""

import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Configure gateway intents.
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

# Load variables from '.env' file into the environment.
load_dotenv()

# Get the Discord token from the environment.
discord_token = os.getenv('DISCORD_TOKEN')

# Configure the bot. The 'command_prefix' parameter is required
# but it's not being used so we set it to something random.
bot = commands.Bot(command_prefix='(╯°□°)╯', intents=intents)

# Load the first cog located at 'cog/bot.py'.
asyncio.run(bot.load_extension('cog.bot'))

# Run the bot.
bot.run(discord_token)
