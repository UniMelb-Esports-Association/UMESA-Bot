"""Handles creating tickets for clip submission
"""
from ..ticket_module import TicketModule
from discord.ext import commands

TICKET_PREFIX = "clip"
EMBED_PATH = "cog/ticket/clip_questions.json"

class ClipTicket(TicketModule):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot, TICKET_PREFIX, EMBED_PATH)
        
async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the ticket cog.
    Also stores an instance of itself within the Discord bot instance for
    future reference

    Args:
        bot: The bot to add this cog to.
    """
    instance = ClipTicket(bot)
    bot.instances[TICKET_PREFIX] = instance
    await bot.add_cog(instance)