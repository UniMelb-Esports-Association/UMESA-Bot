"""Handles creating/deleting tickets

This is a generic interface intended to be used as an abstract class. For
specific functionality, another Cog should be created and inherit this class.
"""

from .ticket_data import Ticket_Data

import discord
from discord.ext import commands


class TicketManagement(commands.Cog):
    """A class to manage ticket creation/deletion
    
    Args:
        bot: The bot to add this cog to.
    """
    
    def __init__(self, bot: commands.Bot) -> None:
        
        self.bot = bot
        self._guild = bot.guilds[0]
        
    async def send_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed
    ) -> None:
        """Sends an embed to the channel where the method was called
        
        Args:
            interaction: The interaction object for the slash command
            embed: embed object to be sent
        """
        
        await interaction.channel.send(embed=embed)
    
    async def send_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ) -> None:
        """Sends a button to the channel where the method was called
        
        Args:
            interaction: The interaction object for the slash command
            button: button object to be sent
        """
        
        # add button to View() so it can be displayed
        view = discord.ui.View(timeout=None)
        view.add_item(button)
        
        await interaction.channel.send(view=view)
    
    async def create_channel(
        self,
        name: str,
        category_id: int,
        permissions: dict
    ) -> None:
        """Creates a new channel in a specified category and add the user who
            initiated the interaction
        
        Args:
            interaction: The interaction object for the slash command
            name: Name of the channel
            category_id: Id of the new channel's category
            permissions: Dictionary of {user: discord.PermissionsOverwrite}
        """
        
        category = discord.utils.get(self._guild.categories, id=category_id)
        await self._guild.create_text_channel(
            name,
            category=category,
            overwrites=permissions)
        
        
async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the TicketManagement cog
    and its children.

    Args:
        bot: The bot to add this cog to.
    """
    
    module_names = Ticket_Data().module_names()
    
    for module in module_names:
        await bot.load_extension(f'cog.ticket.{module["file_name"]}')

    await bot.add_cog(TicketManagement(bot))