"""Handles creating tickets for general ticket submission
"""
from ..ticket_module import TicketModule
from discord.ext import commands

TICKET_PREFIX = "general"
EMBED_PATH = None

class GeneralTicket(TicketModule):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot, TICKET_PREFIX, EMBED_PATH)
        
async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the ticket cog.
    Also stores an instance of itself within the Discord bot instance for
    future reference

    Args:
        bot: The bot to add this cog to.
    """
    instance = GeneralTicket(bot)
    bot.instances[TICKET_PREFIX] = instance
    await bot.add_cog(instance)