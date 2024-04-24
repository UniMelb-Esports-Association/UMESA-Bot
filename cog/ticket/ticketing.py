"""Handles creating/deleting tickets

This is a generic interface intended to be used as an abstract class. For
specific functionality, another Cog should be created and inherit this class.
"""

import discord
from discord.ext import commands

class TicketManagement(commands.Cog):
    """A class to manage ticket creation/deletion
    
    Args:
        bot: The bot to add this cog to.
    """
    
    def __init__(self, bot: commands.Bot) -> None:
        
        self.bot = bot
        
    async def send_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed
    ) -> None:
        """Sends an embed to the channel where the method was called
        
        Args:
            interaction: The interaction object for the slash command
            embed: embed to be sent
        """
        
        await interaction.channel.send(embed=embed)
    
        
        
async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the TicketManagement cog.

    Args:
        bot: The bot to add this cog to.
    """

    await bot.add_cog(TicketManagement(bot))