"""Handles creating tickets for clip submission

Inherited functions from ticket.py
"""
from __future__ import annotations

from .ticketing import TicketManagement

import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime, timedelta, timezone
import time
import re

class ClipTicketManagement(TicketManagement):
    """A class to manage ticket creation/deletion for clips

    Args:
        bot: The bot to add this cog to.
    """

    def __init__(self, bot: commands.Bot) -> None:

        super().__init__(bot)
        
        self._bot = bot
        # get all used ticket ids
        self._used_ticket_ids = [
            int(channel.name[-3:])
            for channel in self._category.channels]

         
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

    @app_commands.command(name="ticket_booth")
    async def ticket_booth(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """Sends an embed based on given parameter

        Args:
            interaction: The interaction object for the slash command
        """
        
        if not self.check_user_permission(interaction.user):
            await interaction.response.send_message(
                "Insufficient permissions", ephemeral=True
            )
            return
        
        await interaction.response.send_modal(TicketBoothParameters(self))
    
    async def create_ticket_booth(
        self,
        interaction: discord.Interaction,
        embed_title: str,
        embed_text: str,
        button_label: str,
        button_emoji: str,
        embed_colour: int=None
    ) -> None:
        """Generate and send embed/button in Discord
        
        Args:
            interaction: The interaction object for the slash command
            embed_title: title of the embed
            embed_text: description of the embed
        """

        embed = self.create_embed(embed_title, embed_text, embed_colour)
        await self.send_embed(interaction.channel, embed)
        view = discord.ui.View(timeout=None)
        view.add_item(TicketButton(self, button_label, button_emoji))
        try:
           await self.send_view(interaction.channel, view)
        except:
            await interaction.response.send_message(
                "ERROR: Invalid emoji, try again", ephemeral=True)
            return
        await interaction.response.send_message(
            "Ticket booth created", ephemeral=True)
    
    async def create_ticket(
        self, 
        interaction: discord.Interaction,
        ) -> None:
        """Creates a new ticket

        Args:
            interaction: The interaction object for the slash command
        """
        
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        num_tickets_opened = 0
        member_roles = [role.id for role in interaction.user.roles]
        
        # ignore maximum tickets for allowed users (specified in ticketing.py)
        if self._admin_role not in member_roles:
            for channel in self._category.channels:
                if interaction.user in channel.members:
                    num_tickets_opened += 1

        # check if user more tickets opened than allowed
        if num_tickets_opened >= self._max_tickets_per_user:
            await interaction.response.send_message(
                "ERROR: Maximum number of tickets opened", ephemeral=True)
            return

        permission = discord.PermissionOverwrite(view_channel=True)
        ticket_id = self.get_next_ticket_id()
        channel = await self.create_channel(
            f"ticket-{ticket_id:03d}",
            self._category_id,
            interaction.user,
            permission
        )
        self._used_ticket_ids.append(ticket_id)
        
        embeds = self.load_embed("cog/ticket/clip_questions.json")
        
        for embed in embeds:
            await self.send_embed(channel, embed)
        await channel.send(f"{interaction.user.mention}")
        await self.send_view(channel, HideButton())
        await interaction.edit_original_response(content="Ticket created")
    
    @app_commands.command(
        name="ticket_cleanup",
        description="deletes all tickets older than 2 weeks"
    )
    async def clean_tickets(self, interaction) -> None:
        """Delete all tickets with the last message sent before the stale time.
        Note this method uses channel.history not channel.last_message as
        channel.last_message may point to a deleted message which throws an 
        error
        
        Args:
            interaction: The interaction object for the slash command
        """
        
        # check user permissions
        if not self.check_user_permission(interaction.user):
            await interaction.response.send_message(
                "Insufficient permissions", ephemeral=True
            )
            return
        
        present = datetime.now(timezone.utc)
        stale_date = present - self._time_until_ticket_stale
        tickets_deleted = 0
        
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        for channel in self._category.channels:
            last_message = channel.history(limit=1)
            date = [message.created_at async for message in last_message][0]
            if (date < stale_date):
                await channel.delete()
                tickets_deleted += 1
            
        await interaction.followup.send(
            f"{tickets_deleted} ticket(s) deleted")
        
        
class TicketButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r'make_ticket:([0-9]+)'):
    """Dynamic, persistent button to handle ticket creation"""
    
    def __init__(self, ticket_manager, label=None, emoji=None):
        self._ticket_manager = ticket_manager
        super().__init__(
            discord.ui.Button(
                label=label,
                emoji=emoji,
                style=discord.ButtonStyle.blurple,
                custom_id=f"make_ticket:{int(time.time())}"
            )
        )

    @classmethod
    async def from_custom_id(cls,
                             interaction: discord.Interaction,
                             item: discord.ui.Button, 
                             match: re.Match[str]):
        time = int(match.group(1))
        ticket_manager = interaction.client.ticket_manager_instance
        return cls(ticket_manager)

    async def callback(self, interaction):
        await self._ticket_manager.create_ticket(interaction)

        
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
        
    
class TicketBoothParameters(discord.ui.Modal):
    """Set parameters for ticket booth here"""
    
    def __init__(
        self, 
        ticket_manager: ClipTicketManagement
    ) -> None:

        super().__init__()
        self._ticket_manager = ticket_manager
        
    # Questions in form
    title = "Configure ticket booth"
    embed_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Title", 
        placeholder="Name of the ticket"
    )
    embed_text = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Description", 
        placeholder="What is this ticket for?"
    )
    button_title=discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=True,
        label="Button Title", 
        placeholder="Text on button"
    )
    button_emoji=discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=False,
        default=None,
        label="Button Emoji", 
        placeholder="Emoji on button"
    )
    embed_colour = discord.ui.TextInput(
        style=discord.TextStyle.short,
        required=False,
        default=None,
        label="Colour",
        placeholder="Hex colour code (starts with # or 0x)"
    )
    async def on_submit(self, interaction: discord.Interaction):
        

        emoji = self.button_emoji.value
        if not emoji:
            emoji = None
            
        # handle colour code
        colour = self.embed_colour.value
        colour = colour.lstrip("#")
        colour = colour.lstrip("0x")
        
        if not colour:
            colour = None
        else:
            if len(colour) != 6:
                await interaction.response.send_message(
                    "Hexcode must have 6 characters", ephemeral=True)
            else:     
                try:
                    colour = int(colour, 16)
                except:
                    await interaction.response.send_message(
                        "Hexcode not valid", ephemeral=True)
                    return
        
        await self._ticket_manager.create_ticket_booth(
                interaction,
                self.embed_title.value,
                self.embed_text.value,
                self.button_title.value,
                emoji,
                colour,
            )

async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the ClipTicketManagement cog.
    This setup hook also handles intialising the View to ensure
    that any created buttons will still work after the bot restarts

    Args:
        bot: The bot to add this cog to.
    """
    instance = ClipTicketManagement(bot)
    bot.add_view(HideButton())
    # store instance of ClipTicketManagement to be used in TicketButton
    bot.ticket_manager_instance = instance 
    bot.add_dynamic_items(TicketButton)
    await bot.add_cog(instance)