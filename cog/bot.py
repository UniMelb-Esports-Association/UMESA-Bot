"""The entry point for the bot's logic.

Mainly just loads all other cogs and syncs the
command tree when the bot is ready.
"""

from discord.ext import commands


# The list of cogs to load.
_COGS = ('room', 'channel.management', 'channel.assignment', 'misc', 'membership')


class Bot(commands.Cog):
    """A class to handle general bot things.

    Attributes:
        bot: The bot to add this cog to.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Sets up the bot when it is ready to do so."""

        # Load all other cogs after the bot is ready.
        for cog in _COGS:
            await self._bot.load_extension(f'cog.{cog}')

        # Sync the command tree to all guilds.
        await self._bot.tree.sync()

        # Log that the bot is ready.
        ready_msg = f'{self._bot.user} is ready!'
        print(ready_msg)
        print('-' * len(ready_msg))


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the Bot cog.

    Args:
        bot: The bot to add this cog to.
    """

    await bot.add_cog(Bot(bot))
