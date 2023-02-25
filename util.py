"""Contains functions that are useful throughout the program."""

import discord


async def get_nth_msg(
    self,
    channel: discord.TextChannel | discord.Thread,
    n: int
) -> None:
    """Get the nth message in a text channel or thread.

    Args:
        channel: The text channel or thread.
        n: The nth message to get.
    """

    return [
        msg async for msg in channel.history(
            limit=n,
            oldest_first=True
        )
    ][n - 1]
