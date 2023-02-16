"""This is the entry point of the program and it configures and runs the bot.

The Discord authentication token is loaded into the environment from
the '.env' file located in the root of the project. The bot only
loads the 'bot' cog (located in 'cog/bot') here as the entry point
for the bot's logic.
"""

import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Configure gateway intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

# Load variables from '.env' file into the environment
load_dotenv()

# Get the Discord token from the environment
discord_token = os.getenv('DISCORD_TOKEN')

# Configure the bot
# The 'command_prefix' parameter is required but it's not being used
# so we set it to something random
bot = commands.Bot(command_prefix='(╯°□°)╯', intents=intents)
asyncio.run(bot.load_extension('cog.bot'))

# Run the bot
bot.run(discord_token)

# Configure created forum channel to use role for visibility
# Change bot add endpoints to edit mentions
# Change order of threads joined and/or change sort order of forum channels
# Change registed message in forum threads
# Clean up code and comments
