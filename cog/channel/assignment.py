"""Handles assigning members to games.

When a member gives themself a game role, they must be
provided access to all the relevant threads for that
role's game. This functionality is provided here.
"""

import discord
from discord.ext import commands
from data import Data, MISC_GAMES_FORUM_NAME


class ChannelAssignment(commands.Cog):
    """A class to manage forum thread assignment.

    Attributes:
        bot: The bot to add this cog to.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        self._guild = bot.guilds[0]
        self._data = Data()

    @staticmethod
    def _kebab(str_: str) -> str:
        """Converts a string to kebab case.

        Args:
            str_: The string to convert.

        Returns:
            The given string in kebab case.
        """

        return str_.replace(' ', '-').lower()

    @commands.Cog.listener()
    async def on_member_update(
        self,
        before: discord.Member,
        after: discord.Member
    ) -> None:
        """Handles when a member's roles are updated.

        When a member is given a new game role, they are
        added to the threads under the forum associated
        with that role's game.

        Args:
            before: The member object before it was updated.
            after: The member object after it was updated.
        """

        # Determine the IDs of the roles that were added to the member, if any.
        game_role_ids = set(self._data.role_ids())
        before_role_ids = set(role.id for role in before.roles)
        after_role_ids = set(role.id for role in after.roles)
        before_game_role_ids = game_role_ids.intersection(before_role_ids)
        after_game_role_ids = game_role_ids.intersection(after_role_ids)
        added_role_ids = list(after_game_role_ids - before_game_role_ids)

        for id_ in added_role_ids:
            # Get the forum name associated with the added role's game.
            role = self._guild.get_role(id_)
            forum_name = self._kebab(role.name)

            # If the associated forum is 'Miscellaneous Games', then skip
            # it since each thread in this forum is a game of its own and
            # we want members to be able to manually follow which miscellaneous
            # games they play rather than being added to all of them.
            if forum_name == MISC_GAMES_FORUM_NAME:
                continue

            # Get the forum's threads for the added role's game.
            forum_id = self._data.forum_id(forum_name)
            forum_threads = self._guild.get_channel(forum_id).threads

            # Since threads are added to the top of the thread list for
            # their associated forum rather than the bottom, we must reverse
            # the order of the thread list to maintain the order of thread
            # creation in the channel list.
            forum_threads.reverse()

            # Add the member to each thread. It's worth noting that
            # we use a special technique here. We don't use the
            # discord.Thread.add_user method as this sends a system
            # message to every thread the user is added to, which can
            # become annoying and clutter the channel. We also don't
            # send a message in the thread that mentions the member
            # and then delete it immediately as this results in ghost
            # unread indicators. Instead, we edit a message sent by
            # the bot at the thread's creation with a mention, and
            # then edit it again to remove the mention. This adds
            # the member to the thread, does not give them a ghost
            # ping and does not send a notification.
            for thread in forum_threads:
                # Get the second message ever sent in the thread,
                # which is the message sent by the bot at the
                # thread's creation.
                bot_message = [
                    msg async for msg in thread.history(
                        limit=2,
                        oldest_first=True
                    )
                ][1]

                # Edit the bot's message with the mention, and then
                # immediately edit it again to remove the mention.
                old_content = bot_message.content
                new_content = old_content + f' [Adding {after.mention}...]'
                await bot_message.edit(content=new_content)
                await bot_message.edit(content=old_content)


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the ChannelAssignment cog.

    Args:
        bot: The bot to add this cog to.
    """

    await bot.add_cog(ChannelAssignment(bot))
