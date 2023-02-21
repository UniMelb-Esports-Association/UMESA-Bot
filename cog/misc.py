"""Handles miscellaneous functions.

Miscellaneous functions are ones that do not clearly
fit into an already established category and/or
do not contribute to the main goals of the bot.
"""

import discord
from discord import app_commands
from discord.ext import commands
from .channel import assignment


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
        assignment.disable_member_update = True

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

        assignment.disable_member_update = False

    @discord.app_commands.checks.has_role('Admin')
    @app_commands.command(name='fix-message')
    async def fix_message(
        self,
        interaction: discord.Interaction,
        channel: discord.abc.GuildChannel
    ) -> None:
        await interaction.response.defer(thinking=True)

        for thread in channel.threads:
            # Get the first message ever sent in the thread,
            # which is the message sent by the bot at the
            # thread's creation.
            bot_message = [
                msg async for msg in thread.history(
                    limit=1,
                    oldest_first=True
                )
            ][0]

            await bot_message.edit(
                content=f'Registered game: \'{channel.name.replace("-", " ").upper()}!\''
            )

        await interaction.followup.send('Fixed!')


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the Misc cog.

    Args:
        bot: The bot to add this cog to.
    """

    await bot.add_cog(Misc(bot))
