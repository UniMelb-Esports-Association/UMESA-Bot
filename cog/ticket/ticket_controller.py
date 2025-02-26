"""Controller for all user ticket functionality"""

from .ticket_data import TicketData
from .interactables import HideButton
from .ticketing import TicketManagement

import discord
from discord.ext import commands
from discord import app_commands

from datetime import datetime, timedelta, timezone

TICKET_TYPE_NUM = 4

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
    async def clean_tickets(
        self, 
        interaction: discord.Interaction
        ) -> None:
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
            message = [message async for message in last_message][0]
            date = message.created_at
            
            # delete messages older than stale_date or empty tickets
            # last message was the hide button sent by the bot
            if date < stale_date or message.components:
                await channel.delete()
                tickets_deleted += 1
            
        await interaction.followup.send(
            f"{tickets_deleted} ticket(s) deleted")
    
    @app_commands.command(name="ticket_booth")
    async def ticket_booth(
        self,
        interaction: discord.Interaction,
        embed_title: str,
        embed_text: str,
        embed_colour: str=""
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
        
        if not embed_colour:
            embed_colour = None
        else:
            if len(embed_colour) != 6:
                await interaction.response.send_message(
                    "Hexcode must have 6 characters", ephemeral=True)
                return
            else:     
                try:
                    embed_colour = int(embed_colour, 16)
                except:
                    await interaction.response.send_message(
                        "Hexcode not valid", ephemeral=True)
                    return

        await interaction.response.send_modal(
            TicketBoothParameters(self, embed_title, embed_text, embed_colour)
            )
        
    async def create_ticket_booth(
        self,
        interaction: discord.Interaction,
        embed_title: str,
        embed_text: str,
        embed_colour: int|None,
        button_labels: list[str]
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
        
        # loop through instances and button labels
        
        for instance, label in zip(self.bot.instances.values(), button_labels):
            button = instance.get_ticket_button(label)
            view.add_item(button)
            
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
        ticket_manager: TicketController,
        embed_title: str,
        embed_text: str,
        embed_colour: str=None
    ) -> None:

        super().__init__(title="Configure ticket booth")
        self._ticket_manager = ticket_manager
        self._embed_title = embed_title
        self._embed_text = embed_text
        self._embed_colour = embed_colour
        
        ticket_types = list(self._ticket_manager.bot.instances.keys())
        
        # Create a new field for each TICKET_TYPE_NUM
        # NOTE: Discord Modals only have a maximum of 5 fields
        for i in range(TICKET_TYPE_NUM):
            button_title = discord.ui.TextInput(
            style=discord.TextStyle.short,
            required=True,
            label=f"Button Title: {ticket_types[i]}", 
            placeholder="Text on button"
            )
            self.add_item(button_title)
    
    async def on_submit(self, interaction: discord.Interaction):
        
        button_labels = [item.value for item in self.children]
        
        await self._ticket_manager.create_ticket_booth(
                interaction,
                self._embed_title,
                self._embed_text,
                self._embed_colour,
                button_labels
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
            await bot.load_extension(f'cog.ticket.modules.{module}')