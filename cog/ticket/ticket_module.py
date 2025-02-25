"""Generic class for new ticket types"""

from __future__ import annotations

from .ticketing import TicketManagement

import discord
from discord.ext import commands

import time
import re

class TicketModule(TicketManagement):
    """Generic class to create new ticket
    """

    def __init__(self, 
                 bot: commands.Bot,
                 ticket_prefix: str,
                 embed_path: str,
                 ) -> None:

        super().__init__(bot)
        
        self._bot = bot
        self._ticket_prefix = ticket_prefix
        self._embeds = self.load_embed(embed_path)
        # get all currently used ticket ids
        self._used_ticket_ids = [
            int(channel.name[-3:])
            for channel in self._category.channels
            if self._ticket_prefix in channel.name]
        bot.add_dynamic_items(self.TicketButton)
    
    def get_ticket_button(self, label=None, emoji=None) -> discord.Button:
        return self.TicketButton(self, label, emoji)

    class TicketButton(
        discord.ui.DynamicItem[discord.ui.Button],
        template=r'(?P<prefix>[a-z]+):[0-9]+'):
            """Dynamic, persistent button to handle ticket creation"""
            
            def __init__(self, ticket_manager, label=None, emoji=None):
                self._ticket_manager = ticket_manager
                super().__init__(
                    discord.ui.Button(
                        label=label,
                        emoji=emoji,
                        style=discord.ButtonStyle.blurple,
                        custom_id=f"{ticket_manager._ticket_prefix}:{int(time.time())}"
                    )
                )

            @classmethod
            async def from_custom_id(cls,
                                    interaction: discord.Interaction,
                                    item: discord.ui.Button, 
                                    match: re.Match[str]):
                prefix = match["prefix"]
                ticket_manager = interaction.client.instances[prefix]
                return cls(ticket_manager)

            async def callback(self, interaction):
                await self._ticket_manager.create_ticket(interaction)