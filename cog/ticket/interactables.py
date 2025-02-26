"""Stores all discord.Interaction objects

Currently has buttons and modals
"""

import discord
import re
import time

class HideButton(discord.ui.View):
    """View to store hide channel button
    
    This view is used to ensure that when the bot restarts, all currently
    sent buttons will still function
    """
    
    label = "Close submission"
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