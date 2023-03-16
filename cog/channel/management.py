"""Handles channel management relating to game channels and their threads.

When a game's channel is created by an admin, it must be registered
as a game channel and an associated role must be created for it. This
and related functonality is provided here.
"""

import asyncio

import discord
from discord.ext import commands, tasks

from data import Data

# These constants are valid (and used) values for a
# thread's auto archive duration and a text channel's
# default auto archive duration.
THREE_DAYS_IN_MINS = 4320
ONE_WEEK_IN_MINS = 10080


class ChannelManagement(commands.Cog):
    """A class to manage game channel and thread creation/deletion.

    Attributes:
        bot: The bot to add this cog to.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        self._guild = bot.guilds[0]
        self._data = Data()
        self._keep_alive.start()

    @staticmethod
    def _title(str_: str) -> str:
        """Converts a string from kebab case to title case.

        Args:
            str_: The string to convert.

        Returns:
            The given kebab case string in title case.
        """

        return str_.replace('-', ' ').title()

    @commands.Cog.listener()
    async def on_guild_channel_create(
        self,
        channel: discord.abc.GuildChannel
    ) -> None:
        """Handles when a game channel is created.

        Args:
            channel: The channel that was created.
        """

        # If a channel is created outside of the 'Gaming'
        # or 'Team' category, then ignore it.
        if channel.category_id not in (
            self._data.gaming_category_id,
            self._data.team_category_id
        ):
            return

        # Make the default auto archive duration for threads
        # in the channel 1 week (the maximum).
        await channel.edit(
            default_auto_archive_duration=ONE_WEEK_IN_MINS
        )

        # Deny @everyone from viewing the channel, sending messages
        # and creating threads.
        await channel.set_permissions(
            self._guild.default_role,
            view_channel=False,
            send_messages=False,
            create_public_threads=False,
            create_private_threads=False
        )

        # Create a new role associated with the channel and
        # give it permission to view the channel.
        game_name = self._title(channel.name)
        new_role = await self._guild.create_role(name=game_name)
        await channel.set_permissions(
            new_role,
            view_channel=True
        )

        # Add the newly created channel to the data file.
        self._data.add_game(
            channel.name,
            new_role.id,
            channel.id
        )

        # Send a message to the log channel saying that
        # the game has been added successfully.
        log_channel = self._guild.get_channel(
            self._data.log_channel_id
        )
        await log_channel.send(f'Registered channel: \'{game_name.upper()}\'')

    @commands.Cog.listener()
    async def on_guild_channel_delete(
        self,
        channel: discord.abc.GuildChannel
    ) -> None:
        """Handles when a game channel is deleted.

        Args:
            channel: The channel that was deleted.
        """

        # If a channel is deleted outside of the 'Gaming'
        # or 'Team' category, then ignore it.
        if channel.category_id not in (
            self._data.gaming_category_id,
            self._data.team_category_id
        ):
            return

        # Delete the role [THIS HAS BEEN DEEMED TOO RISKY].
        # role_id = self._data.role_id(channel.name)
        # role = self._guild.get_role(role_id)
        # await role.delete()

        # Delete the data file entry.
        self._data.delete_game(channel.name)
        log_channel = self._guild.get_channel(
            self._data.log_channel_id
        )

        # Send a message to the log channel saying that
        # the game has been deleted successfully.
        game_name = self._title(channel.name)
        await log_channel.send(
            f'Unregistered channel: \'{game_name.upper()}\''
        )

    @commands.Cog.listener()
    async def on_thread_create(
        self,
        thread: discord.Thread
    ) -> None:
        """Handles when a game channel's thread is created.

        Args:
            thread: The thread that was created.
        """

        # If the thread's parent channel is not a game channel,
        # then ignore it.
        if thread.parent_id not in self._data.channel_ids():
            return

        # Sleep for 5 seconds to allow the first message to
        # be automatically sent in the thread by it's author.
        await asyncio.sleep(5)

        # Send a message to the created thread saying that
        # it was successfully registered with the game. This
        # message is also edited later with a mention
        # to add a member to the thread without any notification.
        await thread.send(
            f'Registered this thread with '
            f'\'{self._title(thread.parent.name).upper()}\'!'
        )

    @commands.Cog.listener()
    async def on_thread_delete(
        self,
        thread: discord.Thread
    ) -> None:
        """Handles when a game channel's thread is deleted.

        Args:
            thread: The thread that was deleted.
        """

        # If the thread's parent channel is not a game channel,
        # then ignore it.
        if thread.parent_id not in self._data.channel_ids():
            return

        # Send a message to the log channel saying that the
        # thread has been unregistered from the game.
        log_channel = self._guild.get_channel(self._data.log_channel_id)
        await log_channel.send(
            f'Unregistered the \'{thread.name}\' thread '
            f'from \'{self._title(thread.parent.name).upper()}\'!'
        )

    @tasks.loop(hours=24)
    async def _keep_alive(self) -> None:
        """Stops all game threads from automatically archiving.

        It does this by changing the automatic archive duration
        on each game thread and then changing it back, which
        resets the timer. The automatic archive duration is changed
        everytime the bot starts up and then every 24 hours afterwards.
        """

        # Get all the game threads.
        threads = filter(
            lambda thread: thread.parent_id in self._data.channel_ids(),
            self._guild.threads
        )

        # Change the auto archive duration for each thread, and then
        # change it back again.
        for thread in threads:
            await thread.edit(auto_archive_duration=THREE_DAYS_IN_MINS)
            await thread.edit(auto_archive_duration=ONE_WEEK_IN_MINS)


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the ChannelManagement cog.

    Args:
        bot: The bot to add this cog to.
    """

    await bot.add_cog(ChannelManagement(bot))
