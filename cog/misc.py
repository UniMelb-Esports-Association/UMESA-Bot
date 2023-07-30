"""Handles miscellaneous functions.

Miscellaneous functions are ones that do not clearly
fit into an already established category and/or
do not contribute to the main goals of the bot.
"""

import discord
from discord import app_commands
from discord.ext import commands

import codecs
import requests
import csv
from contextlib import closing

from .channel import assignment
from util import get_nth_msg
from data import MISC_GAMES_CHANNEL_NAME


class Misc(commands.Cog):
    """A class to manage miscellaneous functions.

    Attributes:
        bot: The bot to add this cog to.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        self._guild = bot.guilds[0]

    @discord.app_commands.checks.has_role('Admin')
    @app_commands.command(name='add-members')
    async def add_members(
        self,
        interaction: discord.Interaction,
        role_from: discord.Role,
        role_to: discord.Role
    ) -> None:
        """Adds members from one role to another.

        This is a convenience method for times when it's needed,
        such as when migrating from the old game roles to the
        new ones.

        Args:
            interaction: The interaction object for the slash command.
            role_from: The role to add members from.
            role_to: The role to add members to.
        """

        # Flag that the on_member_update event should be disabled,
        # because otherwise a new member update event is fired each
        # time a new role is assigned which rapidly leads to too many
        # operations happening at the same time and rate limiting.
        assignment.set_member_update_state(False)

        # Defer the bot's response to give time for
        # the members to be added to the role.
        await interaction.response.defer(thinking=True)

        # Add the members to the role.
        for member in role_from.members:
            await member.add_roles(role_to)

        # Stop deferring and report that the bot has finished.
        await interaction.followup.send(
            f'Successfully added members from '
            f'{role_from.mention} to {role_to.mention}!'
        )

        # Flag that the on_member_update event can be enabled again.
        assignment.set_member_update_state(True)

    @discord.app_commands.checks.has_role('Admin')
    @app_commands.command(name='fix-message')
    async def fix_message(
        self,
        interaction: discord.Interaction,
        channel: discord.abc.GuildChannel,
    ) -> None:
        """Replaces a broken bot message with it's original content.

        Sometimes when members are added too quickly to a thread, the
        bot message that is edited with a mention to add them gets
        clogged with member mentions. This manually fixes all those
        messages for all threads in a channel by replacing the content
        of the bot message with what it was originally.

        Args:
            interaction: The interaction object for the slash command.
            channel: The channel with the threads that have messages to fix.
        """

        # Defer the bot's response to give time for
        # the fix to complete.
        await interaction.response.defer(thinking=True)

        is_misc = channel.name == MISC_GAMES_CHANNEL_NAME
        for thread in channel.threads:
            # Get the first message ever sent in the thread,
            # which is the message sent by the bot at the
            # thread's creation.
            bot_message = await get_nth_msg(thread, 2 if is_misc else 1)

            # The original content of the bot message.
            og_content = (
                f'Registered this thread with '
                f'\'{channel.name.replace("-", " ").upper()}\'!'
            )

            # Replace the bot message with it's original content.
            await bot_message.edit(content=og_content)

        # Stop deferring and report that the bot has finished.
        await interaction.followup.send('Fixed!')

    @discord.app_commands.checks.has_role('Admin')
    @app_commands.command(name='update-membership')
    async def update_membership(
        self,
        interaction: discord.Interaction,
        customisations_csv: discord.Attachment,
        role: discord.Role
    ) -> None:
        """Adds members from an UMSU customisations file to a role.

        Args:
            interaction: The interaction object for the slash command.
            customisations_csv: The members customisations csv file.
            role: The membership role to add members to.
        """

        # Defer the bot's response to give time for
        # the members to be added to the role.
        await interaction.response.defer(thinking=True)

        # Download and process the given CSV file and add members to
        # the given role if an unambigious match is found,
        # otherwise report them appropriately.
        no_matches = []
        multiple_matches = []
        with closing(requests.get(customisations_csv.url, stream=True)) as r:
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
            for row in reader:
                # If the row doesn't contain enough values to be able
                # to have the information we need, then skip it.
                if len(row) < 7:
                    continue

                # 5 is the index of the questions column.
                if row[5] == 'Discord ID' or row[5] == 'Discord username':
                    # 6 is the index of the answers column.
                    # Here we also remove the tag if it exists
                    # because the query_members method doesn't like it.
                    member_username = row[6].split('#')[0]

                    matching_members = await self._guild.query_members(
                        query=member_username
                    )
                    match len(matching_members):
                        case 0:
                            no_matches.append(member_username)
                        case 1:
                            await matching_members[0].add_roles(role)
                        case _:
                            multiple_matches.append(member_username)

        # Stop deferring and send a summary.
        await interaction.followup.send(
            f'Done!\n\n'
            f'No matches found for: {no_matches}\n\n'
            f'Multiple matches found for: {multiple_matches}'
        )


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the Misc cog.

    Args:
        bot: The bot to add this cog to.
    """

    await bot.add_cog(Misc(bot))
