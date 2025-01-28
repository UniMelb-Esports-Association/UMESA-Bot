"""Handles creating/deleting tickets

This is a generic interface intended to be used as an abstract class. For
specific functionality, another Cog should be created and inherit this class.
"""

from .ticket_data import TicketData

import discord
from discord.ext import commands

import json
from datetime import timedelta

TIME_UNTIL_TICKET_STALE = timedelta(weeks=2)
MAX_TICKETS_PER_USER = 3
MAX_TICKETS = 500
MAX_TICKET_ID = 999

class TicketManagement(commands.Cog):
    """A class to manage ticket creation/deletion
    
    Args:
        bot: The bot to add this cog to.
    """
    
    def __init__(self, bot: commands.Bot) -> None:
        
        self.bot = bot
        self._guild = bot.guilds[0]
        
        self._data = TicketData()
        self._category_id = (
            self._data.module("clip")["category_id"]
        )
        self._category = discord.utils.get(
            self.bot.guilds[0].categories, id=self._category_id
        )
        self._admin_role = self._data.module("clip")["role_id"]
        self._max_tickets_per_user = MAX_TICKETS_PER_USER
        self._time_until_ticket_stale = TIME_UNTIL_TICKET_STALE
        self._used_ticket_ids = []
        
    async def send_embed(
        self,
        channel: discord.channel,
        embed: list
    ) -> None:
        """Sends an embed to the channel where the method was called
        
        Args:
            channel: channel to send embed to
            embed: embed object to be sent
        """
        
        await channel.send(embed=embed)
        
    def load_embed(
        self,
        filepath: str,
    ) -> None:
        """Loads embed(s) from file
        
        Args:
            filepath: filepath to json where embed data is stored
            
        Returns:
            List of embeds
        """
    
        with open(filepath, "r") as file:
            data = json.load(file)
            
        embeds = []
        

        for embed in data["embeds"]:
            test = discord.Embed.from_dict(embed)
            embeds.append(test)
        
        return embeds
    
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
    
    def get_next_ticket_id(self):
        """Retrieves the next valid ticket Id
        Finds Id based on the following:
        Get highest ticket number possible, or
        start from Id=1 and increment until unused id is found
        
        Naively assumes that there will always be an available id 
        (MAX_TICKET_ID > MAX_TICKETS)
        
        Returns:
            Ticket Id
        """
        
        if not self._used_ticket_ids:
            return 1
        
        ticket_id = self._used_ticket_ids[-1]
        
        while ticket_id in self._used_ticket_ids:
            if ticket_id == self._used_ticket_ids:
                ticket_id = 1
            else:
                ticket_id += 1
        
        return ticket_id
    
    def check_user_permission(self, user: discord.User) -> bool:
        """Checks whether the user has the admin role
        
        Args:
            user: user whose roles are checked
            
        Returns:
            Boolean
        """
        
        user_roles = [role.id for role in user.roles]
        
        if self._admin_role in user_roles:
            return True
        
        return False
    
    async def create_ticket(
        self, 
        interaction: discord.Interaction,
        embeds: list[discord.Embed] = None
        ) -> None:
        """Creates a new ticket

        Args:
            interaction: The interaction object for the slash command
            embeds: Embeds to send to the new channel
        """
        
        permission = discord.PermissionOverwrite(view_channel=True)
        ticket_id = self.get_next_ticket_id()
        channel = await self.create_channel(
            f"{self._ticket_prefix}-{ticket_id:03d}",
            self._category_id,
            interaction.user,
            permission
        )
        self._used_ticket_ids.append(ticket_id)
        
        for embed in embeds:
            await self.send_embed(channel, embed)
        await channel.send(f"{interaction.user.mention}")
        await self.send_view(channel, HideButton())


class HideButton(discord.ui.View):
    """View to store hide channel button
    
    This view is used to ensure that when the bot restarts, all currently
    sent buttons will still function
    """
    
    label = "Close ticket"
    emoji = "⚠️"
    style = discord.ButtonStyle.danger
    
    def __init__(
        self
    ) -> None:
        super().__init__(timeout=None)
        
    @discord.ui.button(custom_id="ticket_hider",
                       label=label,
                       emoji=emoji,
                       style=style)
    async def activate(
        self,
        interaction: discord.Interaction,
        button: discord.Button
    ) -> None:
        """Hide the channel from non-moderator users when pressed
        
        This function syncs the channel with the category permissions
        Args:
        interaction: The interaction object created by button
        button: Required by Discord interaction but not used here
        """
        await interaction.response.send_message("Closing ticket...")
        await interaction.channel.edit(sync_permissions=True)
        # Check if the ticket was empty (second last message was from this bot)
        # Ignores the closing ticket message.
        last_message = interaction.channel.history(limit=2)
        user = [message.author async for message in last_message][1]
        if user == interaction.client.user:
            await interaction.channel.delete()
             
        
async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the TicketManagement cog
    and its children.

    Args:
        bot: The bot to add this cog to.
    """
    
    module_names = TicketData().module_names()
    bot.add_view(HideButton())
    
    for module in module_names:
        await bot.load_extension(f'cog.ticket.{module}')

    await bot.add_cog(TicketManagement(bot))