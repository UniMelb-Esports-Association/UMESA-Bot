"""Handles creating tickets for clip submission

Inherited functions from ticket.py
"""
from __future__ import annotations

from .ticketing import TicketManagement

import discord
from discord import app_commands
from discord.ext import commands

import time
import re

TICKET_PREFIX = "clip"
EMBED_PATH = "cog/ticket/clip_questions.json"

class ClipTicketManagement(TicketManagement):
    """A class to manage ticket creation/deletion for clips

    Args:
        bot: The bot to add this cog to.
    """

    def __init__(self, bot: commands.Bot) -> None:

        super().__init__(bot)
        
        self._bot = bot
        self._ticket_prefix = TICKET_PREFIX
        # get all currently used ticket ids
        self._used_ticket_ids = [
            int(channel.name[-3:])
            for channel in self._category.channels
            if self._ticket_prefix in channel.name]
        self._embeds = self.load_embed(EMBED_PATH)
    
    def get_ticket_button(self, label, emoji):
        return TicketButton(self, label, emoji)

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
            ticket_manager = interaction.client.instances[TICKET_PREFIX]
            return cls(ticket_manager)

        async def callback(self, interaction):
            await self._ticket_manager.create_ticket(interaction)

async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the ClipTicketManagement cog.
    This setup hook also handles intialising the View to ensure
    that any created buttons will still work after the bot restarts

    Args:
        bot: The bot to add this cog to.
    """
    instance = ClipTicketManagement(bot)
    # store instance of ClipTicketManagement to be used in TicketButton

    bot.instances[TICKET_PREFIX] = instance
    bot.add_dynamic_items(TicketButton)
    await bot.add_cog(instance)