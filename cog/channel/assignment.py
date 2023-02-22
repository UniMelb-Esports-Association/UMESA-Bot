"""Handles assigning members to games.

When a member gives themself a game role, they must be
provided access to all the relevant threads for that
role's game. This functionality is provided here.
"""

import discord
from discord import app_commands
from discord.ext import commands
from data import Data, MISC_GAMES_FORUM_NAME

# The maximum number of members that can be in a role for a
# role mention in a thread to add them all to the thread
_MAX_ROLE_SIZE_FOR_THREAD_JOIN = 99

# A flag to ...
disable_member_update = False


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

    @staticmethod
    async def _add_member_to_threads(
        mention: str,
        threads: [discord.Thread]
    ) -> None:
        """Adds member(s) to a list of threads.

        This is done without any notification being generated
        by the threads.

        Args:
            mention: The mention string to use to add the members.
            threads: The threads to be added to.
        """

        # Since threads are added to the top of the thread list for
        # their associated forum rather than the bottom, we must reverse
        # the order of the thread list to maintain the order of thread
        # creation in the channel list.
        threads = list(threads)
        threads.reverse()

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
        for thread in threads:
            # Get the first message ever sent in the thread,
            # which is the message sent by the bot at the
            # thread's creation.
            bot_message = [
                msg async for msg in thread.history(
                    limit=1,
                    oldest_first=True
                )
            ][0]

            # Edit the bot's message with the mention, and then
            # immediately edit it again to remove the mention.
            old_content = bot_message.content
            new_content = old_content + f' [Adding {mention}...]'
            await bot_message.edit(content=new_content)
            await bot_message.edit(content=old_content)

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
        if disable_member_update:
            return

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

            # Add the member to the forum threads.
            await self._add_member_to_threads(after.mention, forum_threads)

    @discord.app_commands.checks.has_role('Admin')
    @app_commands.command(name='sync')
    async def sync(
        self,
        interaction: discord.Interaction,
        channel: discord.abc.GuildChannel,
        role: discord.Role
    ) -> None:
        """Syncs a role with a game channel's threads.

        Syncing means that every member in a role is added
        to every thread in a game channel in the correct order.

        Args:
            interaction: The interaction object for the slash command.
            channel: The game channel that contains the threads to be added to.
            role: The role that contains the members to add.
        """

        # Defer the bot's response to give
        # time for the sync to complete.
        await interaction.response.defer(thinking=True)

        # Calculate the number of role partitions required to add every member
        # from the role into the game channel's threads. This is done because
        # there is a maximum number of members that can be added to a thread
        # at once. To solve this, we split the members of the role across many
        # temporary roles and then add every member from each temporary role
        # to the game channel's threads.
        partitions = -(len(role.members) // -_MAX_ROLE_SIZE_FOR_THREAD_JOIN)

        # Split the members into temporary roles if required.
        roles_to_add = []
        if partitions == 1:
            roles_to_add.append(role)
        else:
            # Add members in max chunks to the temporary roles
            # until every member from the original role has been
            # allocated to a temporary one.
            for i in range(partitions):
                new_role = await self._guild.create_role(name=role.name)
                start_index = i * _MAX_ROLE_SIZE_FOR_THREAD_JOIN
                end_index = (i + 1) * _MAX_ROLE_SIZE_FOR_THREAD_JOIN
                for member in role.members[start_index:end_index]:
                    await member.add_roles(new_role)

                roles_to_add.append(new_role)

        # Add all members to the game channel threads.
        for role in roles_to_add:
            await self._add_member_to_threads(role.mention, channel.threads)

            # Delete a role if it is temporary
            if len(roles_to_add) > 1:
                await role.delete()

        # Stop deferring and report that the bot has finished.
        await interaction.followup.send(
            f'Finished syncing {role.mention} with {channel.mention}!'
        )


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the ChannelAssignment cog.

    Args:
        bot: The bot to add this cog to.
    """

    await bot.add_cog(ChannelAssignment(bot))
