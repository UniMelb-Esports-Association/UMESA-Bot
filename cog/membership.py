"""Handles management of the membership yearly roles

This role should be reset every year
"""

import discord
from discord import app_commands
from discord.ext import commands

from csv import reader

from .channel import assignment


class Membership(commands.Cog):
    """A class to manage the Membership role.

    Attributes:
        bot: The bot to add this cog to.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        self._guild = bot.guilds[0]

    @discord.app_commands.checks.has_role('Admin')
    @app_commands.command(name='update-membership')
    async def update_membership(
        self,
        interaction: discord.Interaction,
        customisations_csv_file: discord.File,
        role_to: discord.Role
    ) -> None:
        """Adds members from a customisations file from umsu export to the a role.

        Args:
            interaction: The interaction object for the slash command.
            customisations_csv_file: The members customisations list.
            role_to: The membership role to add members to.
        """

        # Flag that the on_member_update event should be disabled,
        # because otherwise a new member update event is fired each
        # time a new role is assigned which rapidly leads to too many
        # operations happening at the same time and rate limiting.
        assignment.set_member_update_state(False)

        # Defer the bot's response to give time for
        # the members to be added to the role.
        await interaction.response.defer(thinking=True)

        # process the given csv file
        # add members to role_to if one match is found
        # otherwise report them appropriately 
        with open(customisations_csv_file.fp, 'r') as file:
            no_matches = []
            matches = []
            multiple_matches = {}
            csv_reader = reader(file)

            for row in csv_reader:
                if row[5] == 'Discord ID':
                    discord_id = row[6]
                    matching_users = await self._bot.query_members(query=discord_id, limit=5)

                    if len(matching_users) == 0:
                        no_matches.append(discord_id)
                    elif len(matching_users) == 1:
                        matches.append(discord_id)
                        await matching_users[0].add_roles(role_to)
                    else:
                        multiple_matches[discord_id] = matching_users

        # Stop deferring and send a summary.
        await interaction.followup.send(
            f'{role_to.mention} successfully given to:'
            f'{matches}'
            f'No matches found for'
            f'{no_matches}'
            f'Multiple matches found for'
            '\n '.join(f'{id} found {multiple_matches[id]}' for id in multiple_matches.keys())
        )

        # Flag that the on_member_update event can be enabled again.
        assignment.set_member_update_state(True)


async def setup(bot: commands.Bot) -> None:
    """A hook for the bot to register the Membership cog.

    Args:
        bot: The bot to add this cog to.
    """

    await bot.add_cog(Membership(bot))
