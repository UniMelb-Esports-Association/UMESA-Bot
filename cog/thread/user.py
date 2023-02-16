"""Contains thread-related events."""

import discord
from discord.ext import commands
from data import Data, MISC_GAMES


class ThreadUser(commands.Cog):
    """A class to manage thread-related things.

    Handles members joining or leaving hub threads,
    as well as keeping threads from automatically archiving.

    Attributes:
        bot: the bot to add this cog to
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        self._guild = bot.guilds[0]
        self._data = Data()

    async def _on_thread_member_change(
        self,
        thread_member: discord.ThreadMember,
        joined: bool
    ) -> None:
        """Handles when a member joins or leaves a thread in the gaming hub.

        When a member joins a hub thread:
        - They will be given a role that provides access to the forum for the
          relevant game
        - They will be added to all threads for that game's forum

        If a member leaves a hub thread:
        - Their role for the relevant game will be removed
        - They will be removed from all threads for that game's forum

        Args:
            thread_member: the member that joined or left the thread
            joined: True if the member joined the thread, False if they left
        """

        current_thread = thread_member.thread

        # If the thread joined or left is not in the gaming hub, ignore it
        if current_thread.parent_id != self._data.hub_channel_id:
            return

        member = self._guild.get_member(thread_member.id)
        game = self._data.game(current_thread.id)
        game_role_id = self._data.role_id(game)
        game_forum_id = self._data.forum_id(game)
        game_role = self._guild.get_role(game_role_id)
        game_forum = self._guild.get_channel(game_forum_id)
        if joined:
            await member.add_roles(game_role)

            # If the hub thread joined is 'Miscellaneous Games',
            # then don't automatically add the member to that game's
            # forum threads (i.e. let them choose manually)
            if game != MISC_GAMES:
                for thread in game_forum.threads:
                    await thread.add_user(member)
        else:
            # If the hub thread left is 'Miscellaneous Games',
            # then don't automatically remove the member from that game's
            # forum threads (i.e. keep their manual choices)
            if game != MISC_GAMES:
                for thread in game_forum.threads:
                    await thread.remove_user(member)

            await member.remove_roles(game_role)

    @commands.Cog.listener()
    async def on_thread_member_join(
        self,
        member: discord.ThreadMember
    ) -> None:
        """Fires when a member joins a thread."""

        await self._on_thread_member_change(member, True)

    @commands.Cog.listener()
    async def on_thread_member_remove(
        self,
        member: discord.ThreadMember
    ) -> None:
        """Fires when a member leaves a thread."""

        await self._on_thread_member_change(member, False)


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the Thread cog."""

    await bot.add_cog(ThreadUser(bot))
