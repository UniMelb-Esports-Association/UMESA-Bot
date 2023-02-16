"""Contains classes dedicated to game-related Discord entities/functions."""

import discord
from data import Data
from discord.ext import commands, tasks


class ThreadAdmin(commands.Cog):
    """A class to help manage game-related discord entities.

    Each game is associated with a hub thread, forum, and role.
    This class provides methods to query these entities and
    other entities for the same game.

    Attributes:
        guild: the guild the entities exist in
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        self._guild = bot.guilds[0]
        self._data = Data()
        self._keep_alive.start()

    @staticmethod
    def _title(str_: str):
        return str_.replace('-', ' ').title()

    @commands.Cog.listener()
    async def on_thread_create(
        self,
        thread: discord.Thread
    ) -> None:
        if thread.parent_id == self._data.hub_channel_id:
            new_role = await self._guild.create_role(name=thread.name)
            category = self._guild.get_channel(
                self._data.gaming_category_id
            )
            new_forum = await category.create_forum(thread.name)
            self._data.add_game(
                thread.name,
                thread.id,
                new_forum.id,
                new_role.id
            )

            log_channel = self._guild.get_channel(
                self._data.log_channel_id
            )
            await log_channel.send(f'Registered game: \'{thread.name}\'')
        elif thread.parent_id in self._data.forum_ids():
            await thread.send(
                f'Registered this \'{thread.name}\' thread '
                f'with \'{self._title(thread.parent.name)}\''
            )

    @commands.Cog.listener()
    async def on_thread_delete(
        self,
        thread: discord.Thread
    ) -> None:
        log_channel = self._guild.get_channel(self._data.log_channel_id)
        if thread.parent_id == self._data.hub_channel_id:
            await self._guild.get_role(
                self._data.role_id(thread.name)
            ).delete()

            self._data.delete_game(thread.name)
            await log_channel.send(f'Unregistered game: \'{thread.name}\'')
        elif thread.parent_id in self._data.forum_ids():
            await log_channel.send(
                f'Unregistered the \'{thread.name}\' thread '
                f'from \'{self._title(thread.parent.name)}\''
            )

    @tasks.loop(hours=24)
    async def _keep_alive(self) -> None:
        """Stops all hub and forum threads from automatically archiving.

        It does this by changing the automatic archive duration
        on each thread, and then changing it back. This resets the timer.
        """

        threads = filter(
            lambda thread: (
                thread.parent_id == self._data.hub_channel_id
                or thread.parent_id in self._data.forum_ids()
            ),
            self._guild.threads
        )

        for thread in threads:
            await thread.edit(auto_archive_duration=4320)  # 3 Days
            await thread.edit(auto_archive_duration=10080)  # 1 Week


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the Games cog."""

    await bot.add_cog(ThreadAdmin(bot))
