"""Contains classes dedicated to game-related Discord entities/functions."""

import discord
from enum import Enum


class Game(Enum):
    RAINBOW_SIX_SIEGE = 1
    NEW_WORLD = 2
    MISC = 3


class Games:
    """A class to help manage game-related discord entities.

    Each game is associated with a hub thread, forum, and role.
    This class provides methods to query these entities and
    other entities for the same game.

    Attributes:
        guild: the guild the entities exist in
    """

    def __init__(self, guild: discord.Guild):
        self._data = {
            Game.RAINBOW_SIX_SIEGE:
            (
                guild.get_thread(1053966918559727616),
                guild.get_channel(1053970177324224513),
                guild.get_role(1067921986837286955),
            ),
            Game.NEW_WORLD:
            (
                guild.get_thread(1053967276526809178),
                guild.get_channel(1053970201764429906),
                guild.get_role(1067922065048469575),
            ),
            Game.MISC:
            (
                guild.get_thread(1053968389699280947),
                guild.get_channel(1053970334220570684),
                guild.get_role(1067922109680062597),
            ),
        }

    def thread(self, game: Game) -> discord.Thread:
        """Get the hub thread for a game."""

        return self._data[game][0]

    def forum(self, game: Game) -> discord.abc.GuildChannel:
        """Get the forum for a game."""

        return self._data[game][1]

    def role(self, game: Game) -> discord.Role:
        """Get the role for game."""

        return self._data[game][2]

    def threads(self) -> list[discord.Thread]:
        """Get all hub threads."""

        return [self.thread(game) for game in Game]

    def forums(self) -> list[discord.abc.GuildChannel]:
        """Get all forums."""

        return [self.forum(game) for game in Game]

    def roles(self) -> list[discord.Role]:
        """Get all roles."""

        return [self.role(game) for game in Game]

    def game(self, id_: int) -> Game:
        """Get the game from a hub thread id, game forum id or game role id."""

        for game, objs in self._data.items():
            if id_ in [obj.id for obj in objs]:
                return game

    def is_thread(self, id_: int) -> bool:
        """Determines if a given id is a hub thread id."""

        for objs in self._data.values():
            if id_ == objs[0].id:
                return True

        return False

    def is_forum(self, id_: int) -> bool:
        """Determines if a given id is a game forum id."""

        for objs in self._data.values():
            if id_ == objs[1].id:
                return True

        return False

    def is_role(self, id_: int) -> bool:
        """Determines if a given is a game role id."""

        for objs in self._data.values():
            if id_ == objs[2].id:
                return True

        return False
