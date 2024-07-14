"""Handles creating tickets for clip submission

Inherited functions from ticket.py
"""
from __future__ import annotations

from .ticketing import TicketManagement
from .ticket_data import TicketData

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
    
    MAX_TICKETS = 500
    MAX_TICKET_ID = 999
    MAX_TICKETS_PER_USER = 3
    BOT = None
    CATEGORY_ID = None
    CATEGORY = None
    ADMIN_ROLE = None
    used_ticket_ids = []

    def __init__(self, bot: commands.Bot) -> None:

        super().__init__(bot)
        self._data = TicketData()
        
        ClipTicketManagement.BOT = bot
        ClipTicketManagement.CATEGORY_ID = self._data.module("clip")["category_id"]
        ClipTicketManagement.CATEGORY = discord.utils.get(
            self.bot.guilds[0].categories, id=ClipTicketManagement.CATEGORY_ID
        )
        ClipTicketManagement.ADMIN_ROLE = self._data.module("clip")["role_id"]
        # get all used ticket ids
        ClipTicketManagement.used_ticket_ids = [
            int(channel.name[-3:])
            for channel in ClipTicketManagement.CATEGORY.channels]
        
    @classmethod    
    def get_next_ticket_id(cls):
        """Retrieves the next valid ticket Id
        Finds Id based on the following:
        Get highest ticket number possible, or
        start from Id=1 and increment until unused id is found
        
        Naively assumes that there will always be an available id 
        (MAX_TICKET_ID > MAX_TICKETS)
        
        Returns:
            Ticket Id
        """
        
        if not cls.used_ticket_ids:
            return 1
        
        ticket_id = cls.used_ticket_ids[-1]
        
        while ticket_id in cls.used_ticket_ids:
            if ticket_id == cls.used_ticket_ids:
                ticket_id = 1
            else:
                ticket_id += 1
        
        return ticket_id

    @discord.app_commands.checks.has_role('Admin')
    @app_commands.command(name="ticket_booth")
    async def ticket_booth(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """Sends an embed based on given parameter

        Args:
            interaction: The interaction object for the slash command
        """

        await interaction.response.send_modal(TicketBoothParameters(self))
    
    async def create_ticket_booth(
        self,
        interaction: discord.Interaction,
        embed_title: str,
        embed_text: str,
        button_label: str,
        button_emoji: str,
        embed_colour: int=None,
 
    ) -> None:
        """Generate and send embed/button in Discord
        
        Args:
            interaction: The interaction object for the slash command
            embed_title: title of the embed
            embed_text: description of the embed
        """

        embed = self.create_embed(embed_text, embed_title, embed_colour)
        await self.send_embed(interaction.channel, embed)
        view = discord.ui.View(timeout=None)
        view.add_item(TicketButton(button_label, button_emoji))
        try:
           await self.send_view(interaction.channel, view)
        except:
            await interaction.response.send_message(
                "Invalid emoji, try again", ephemeral=True)
            return
        await interaction.response.send_message(
            "Ticket booth created", ephemeral=True)
        
    
    @classmethod
    async def create_ticket(cls, interaction, information) -> None:
        """Creates a new ticket

        Args:
            interaction: The interaction object for the slash command
            information: Answers filled out in TicketQuestions modal
        """
        num_tickets_opened = 0
        member_roles = [role.id for role in interaction.user.roles]
        instance = ClipTicketManagement(cls.BOT)
        
        # ignore maximum tickets for allowed users (specified in init)
        if cls.ADMIN_ROLE not in member_roles:
            
            for channel in cls.CATEGORY.channels:
                if interaction.user in channel.members:
                    num_tickets_opened += 1

        # check if user more tickets opened than allowed
        if num_tickets_opened >= cls.MAX_TICKETS_PER_USER:
            await interaction.response.send_message(
                "ERROR: Maximum number of tickets opened", ephemeral=True)
            return

        permission = discord.PermissionOverwrite(view_channel=True)
        ticket_id = cls.get_next_ticket_id()
        channel = await ClipTicketManagement.create_channel(
            instance,
            f"ticket-{ticket_id:03d}",
            cls.CATEGORY_ID,
            interaction.user,
            permission
        )
        cls.used_ticket_ids.append(ticket_id)

        await channel.send(f"Hello, {interaction.user.mention}")
        await channel.send(f"Favourite animal: {information['animal']}")
        
        await ClipTicketManagement.send_view(instance, channel, HideButton())
        
        await interaction.response.send_message(
            "Ticket created", ephemeral=True)
    
    @classmethod
    @commands.Cog.listener()
    async def on_guild_channel_delete(
        cls,
        channel: discord.abc.GuildChannel
    ) -> None:
        """Update the list of used ticket ids when a channel is deleted
        
        Args:
            channel: The channel that was deleted
        """
        
        # Only check for channels in this category
        if channel.category_id != cls.CATEGORY_ID:
            return

    @app_commands.command(
        name="delete_tickets",
        description="deletes all tickets"
    )
    async def delete_ticket(self, interaction) -> None:
        category = discord.utils.get(
            self.bot.guilds[0].categories, id=self._category_id
        )
        num_deleted = 0
        await interaction.response.defer(ephemeral=True)
        for channel in category.channels:
            await channel.delete()
            num_deleted += 1
        await interaction.followup.send(f"{num_deleted} channels deleted")
    
    @discord.app_commands.checks.has_role('Admin')
    @app_commands.command(
        name="ticket_cleanup",
        description="deletes all tickets older than 2 weeks"
    )
    async def clean_tickets(self, interaction) -> None:
        """Delete all tickets with the last message sent over 2 weeks ago
        Note this method uses channel.history not channel.last_message as
        channel.last_message may point to a deleted message which throws an 
        error
        
        Args:
            interaction: The interaction object for the slash command
        """
        
        present = datetime.now(timezone.utc)
        two_weeks_ago = present - timedelta(minutes=1)
        tickets_deleted = 0
        
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        for channel in ClipTicketManagement.CATEGORY.channels:
            last_message = channel.history(limit=1)
            date = [message.created_at async for message in last_message][0]
            if (date < two_weeks_ago):
                await channel.delete()
                tickets_deleted += 1
            
        await interaction.followup.send(
            f"{tickets_deleted} ticket(s) deleted")
        
    @app_commands.command(
        name="custom-button",
        description="choose values for button"
    )
    async def custom_button(
        self,
        interaction: discord.Interaction, 
        label: str, 
        emoji: str
    ) -> None:
        view = discord.ui.View(timeout=None)
        view.add_item(TicketButton(label, emoji))
        await self.send_view(interaction.channel, view=view)
        
        await interaction.response.send_message("Button made", ephemeral=True)
        
        
class TicketButton(discord.ui.DynamicItem[discord.ui.Button], template=r'make_ticket:([0-9]+)'):
    def __init__(self, label=None, emoji=None):
        super().__init__(
            discord.ui.Button(
                label=label,
                emoji=emoji,
                style=discord.ButtonStyle.blurple,
                custom_id=f"make_ticket:{int(time.time())}"
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        time = int(match.group(1))
        return cls(time)

    async def callback(self, interaction):
        await interaction.response.send_modal(TicketQuestions())

        
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
        await interaction.response.defer(
            thinking=True, ephemeral=True)
        await interaction.channel.edit(sync_permissions=True)
        await interaction.followup.send("Done!", ephemeral=True)
    

class TicketQuestions(discord.ui.Modal):
    """Popup form that contains questions"""
    
    title = "Fill this out!"
    animal = discord.ui.TextInput(
        label="What is your favourite animal?", 
        style=discord.TextStyle.short,
        placeholder="Dog"
    )
    
    def __init__(
        self, 
    ) -> None:

        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        
        answers = {}
        answers["animal"] = self.animal
        
        await ClipTicketManagement.create_ticket(
            interaction,
            answers
        )
    
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
    bot.add_dynamic_items(TicketButton)
    await bot.add_cog(instance)