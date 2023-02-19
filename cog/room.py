"""Handles auxillary functions for room management.

Room management refers to the temporary voice channel system.
Although this system is provided by a different bot, extra
functionality is provided to the system here.
"""

import discord
from discord.ext import commands
from data import Data


class Room(commands.Cog):
    """A class that contains room-management-related events.

    Attributes:
        bot: The bot to add this cog to.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        self._guild = bot.guilds[0]
        self._data = Data()

    async def _clear(self) -> None:
        """Clears the 'Modify Room' text channel of any messages.

        This is limited to purging 999 messages (more than enough), and
        does not include the first message which is the 'Commands' message.
        This method exists because the 'Modify Room' text channel is only
        meant for slash commands that return ephemeral responses.
        Hence to remove the clutter, all regular messages should be purged.
        """

        # Get the 'Modify Room' channel
        modify_room_channel = self._guild.get_channel(
            self._data.modify_room_channel_id
        )

        # Purge messages
        await modify_room_channel.purge(
            limit=999,
            check=lambda msg: msg.id != self._data.modify_room_commands_msg_id
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Handles messages sent in the 'Modify Room' text channel.

        Args:
            message: The message that was sent.
        """

        # If a message is sent in the 'Modify Room' text channel, then delete
        # it and any other messages besides the 'Commands' message.
        if message.channel.id == self._data.modify_room_channel_id:
            await self._clear()


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the Room cog.

    Args:
        bot: The bot to add this cog to.
    """

    await bot.add_cog(Room(bot))
