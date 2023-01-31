"""The entry point for the bot's logic.

Mainly just loads all other cogs when the bot is ready.
"""

from discord.ext import commands

# The list of cogs to load
COGS = ('thread', 'room')


class Bot(commands.Cog):
    """A class to handle general bot things.

    Attributes:
        bot: the bot to add this cog to
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Fires when the bot has finished setup."""

        # Load all other cogs after the bot is ready
        for cog in COGS:
            await self._bot.load_extension(f'cog.{cog}')

        # Log that the bot is ready
        ready_msg = f'{self._bot.user} is ready!'
        print(ready_msg)
        print('-' * len(ready_msg))


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the Bot cog."""

    await bot.add_cog(Bot(bot))
