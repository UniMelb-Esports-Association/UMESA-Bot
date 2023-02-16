"""Handles auxillary functions for room management."""

import discord
from discord.ext import commands
from data import Data


class Room(commands.Cog):
    """A class that contains room-management-related events.

    Attributes:
        bot: the bot to add this cog to
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        self._guild = bot.guilds[0]
        self._data = Data()

    async def _clear(self):
        """Clears the 'Modify Room' text channel of any messages.

        This is limited to purging 999 messages (more than enough), and
        does not include the first message which is the 'Commands' message.
        This method exists because the 'Modify Room' text channel is only
        meant for slash commands that return ephemeral responses.
        Hence to remove the clutter, all regular messages should be purged.
        """

        await self._modify_room_channel.purge(
            limit=999,
            check=lambda msg: msg.id != self._data.modify_room_commands_msg_id
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Fires when a message is sent."""

        # If a message is sent in the 'Modify Room' text channel, then delete
        # it and any other messages besides the 'Commands' message
        if message.channel.id == self._data.modify_room_channel_id:
            await self._clear()


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the Room cog."""

    await bot.add_cog(Room(bot))
