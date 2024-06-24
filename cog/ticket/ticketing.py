"""Handles creating/deleting tickets

This is a generic interface intended to be used as an abstract class. For
specific functionality, another Cog should be created and inherit this class.
"""

from .ticket_data import TicketData

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
        channel: discord.channel,
        embed: discord.Embed
    ) -> None:
        """Sends an embed to the channel where the method was called
        
        Args:
            channel: channel to send embed to
            embed: embed object to be sent
        """
        
        await channel.send(embed=embed)
    
    async def send_view(
        self,
        channel: discord.channel,
        view: discord.ui.View
    ) -> None:
        """Sends a view to the channel where the method was called
        
        Args:
            channel: channel to send view to
            view: view object to be sent
        """
        
        await channel.send(view=view)
    
    async def create_channel(
        self,
        name: str,
        category_id: int,
        user_id: int,
        permissions: discord.PermissionOverwrite
    ) -> discord.channel:
        """Creates a new channel in a specified category and add the user who
            initiated the interaction
        
        Args:
            interaction: The interaction object for the slash command
            name: Name of the channel
            user_id: Id of the user who created the interaction
            category_id: Id of the new channel's category
            permissions: permissions in the form of PermissionsOverwrite
            
        Returns:
            The discord.channel object which has been created
        """
        
        category = discord.utils.get(self._guild.categories, id=category_id)
        channel = await self._guild.create_text_channel(
            name,
            category=category)
        await channel.set_permissions(user_id, overwrite=permissions)
        
        return channel
    
    def create_embed(
        self,
        title: str,
        text: str,
        colour: int=None,
    ) -> discord.Embed:
        """Creates an embed with the specified parameters
        
        Args:
            title: Title of the embed
            text: Body text of the embed
        
        Returns:
            Created embed object
        """
        
        embed = discord.Embed()
        embed.title = title
        embed.description = text
        embed.colour=colour
        
        return embed
        
        
async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the TicketManagement cog
    and its children.

    Args:
        bot: The bot to add this cog to.
    """
    
    module_names = TicketData().module_names()
    
    for module in module_names:
        await bot.load_extension(f'cog.ticket.{module["file_name"]}')

    await bot.add_cog(TicketManagement(bot))