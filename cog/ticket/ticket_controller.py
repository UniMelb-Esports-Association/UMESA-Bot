"""Controller for all user ticket functionality"""

from .ticket_data import TicketData
from .interactables import HideButton
from .ticketing import TicketManagement

import discord
from discord.ext import commands
from discord import app_commands

from datetime import datetime, timedelta, timezone

class TicketController(TicketManagement):
    
    """Class to handle bot commands related to ticketing
    
    Args:
        bot: The bot to add this cog to.
    """
    
    def __init__(self, bot: commands.Bot):
        
        super().__init__(bot)

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
        for instance in self.bot.instances.values():
            view.add_item(instance.get_ticket_button(button_label, button_emoji))
        
        #view.add_item(TicketButton(self, button_label, button_emoji))
        try:
           await self.send_view(interaction.channel, view)
        except:
            await interaction.response.send_message(
                "ERROR: Invalid emoji, try again", ephemeral=True)
            return
        await interaction.response.send_message(
            "Ticket booth created", ephemeral=True)


class TicketBoothParameters(discord.ui.Modal):
    """Set parameters for ticket booth here"""
    
    def __init__(
        self, 
        ticket_manager: TicketController
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

async def setup(bot: commands.Bot):
    
    instance = TicketController(bot)
    bot.controller = instance
    await bot.add_cog(instance)
    
    module_names = TicketData().module_names()
    bot.add_view(HideButton())
    bot.instances = {}
    
    for module in module_names:
        if not module == "admin_role":
            await bot.load_extension(f'cog.ticket.{module}')