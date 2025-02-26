"""Handles creating tickets for shop support submission
"""
from ..ticket_module import TicketModule
from discord.ext import commands

TICKET_PREFIX = "shop"

class ShopTicket(TicketModule):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot, TICKET_PREFIX)
        
async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the ticket cog.
    Also stores an instance of itself within the Discord bot instance for
    future reference

    Args:
        bot: The bot to add this cog to.
    """
    instance = ShopTicket(bot)
    bot.instances[TICKET_PREFIX] = instance
    await bot.add_cog(instance)