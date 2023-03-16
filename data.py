"""Handles everything related to the data file.

The data file is a JSON file that stores mappings from
games to the IDs of guild entities such as channels and roles,
as well as other miscellaneous guild entity IDs that the bot
requires to function properly.
"""

import json
from enum import Enum

DATA_FILE = 'data.json'
MISC_GAMES_CHANNEL_NAME = 'misc-games'


class _KEY(Enum):
    """Represents the keys in the data file."""

    GAMING_CATEGORY = 1
    TEAM_CATEGORY = 2
    LOG_CHANNEL = 3
    MODIFY_ROOM_CHANNEL = 4
    MODIFY_ROOM_COMMANDS_MSG = 5
    ROLE = 6
    CHANNEL = 7
    ENTITY = 8

    def __str__(self):
        """Converts a member's name into kebab case."""

        return self.name.replace('_', '-').lower()


class Singleton(type):
    """A singleton metaclass."""

    instance = None

    def __call__(cls, *args, **kw) -> None:
        if not cls.instance:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)

        return cls.instance


class Data(metaclass=Singleton):
    """Handles the persistent data in the data file.

    Provides I/O methods for the data file and parses
    the data to provide convenient attributes and methods
    for accessing the data in common ways.
    """

    def __init__(self) -> None:
        # Load the data file as a dictionary.
        with open(DATA_FILE, 'r') as file:
            self._data = json.load(file)

        # Provide convenience attributes for all keys
        # in the data file so that data lookups don't
        # require magic strings.
        for key, value in self._data.items():
            self.__setattr__(
                key.replace('-', '_')
                + f'{"_id" if key != str(_KEY.ENTITY) else ""}',
                value
            )

    def add_game(
        self,
        name: str,
        role_id: int,
        channel_id: int,
    ) -> None:
        """Adds a game to the data file.

        Args:
            name: The name of the game in kebab case.
            role_id: The ID of the role associated with the game.
            channel_id: The ID of the channel associated with the game.
        """

        # Update the dictionary representation of the data file.
        self.entity[name] = {
            str(_KEY.ROLE): role_id,
            str(_KEY.CHANNEL): channel_id,
        }

        # Write the updated dictionary to the data file.
        with open(DATA_FILE, 'w') as file:
            json.dump(self._data, file, indent=4)

    def delete_game(self, name: str) -> None:
        """Deletes a game from the data file.

        Args:
            name: The name of the game in kebab case.
        """

        # Update the dictionary representation of the data file.
        del self.entity[name]

        # Write the updated dictionary to the data file.
        with open(DATA_FILE, 'w') as file:
            json.dump(self._data, file, indent=4)

    def role_id(self, game: str) -> int:
        """Returns the role ID associated with a game.

        Args:
            game: The name of the game in kebab case.
        """

        return self.entity[game][str(_KEY.ROLE)]

    def channel_id(self, game: str) -> int:
        """Returns the channel ID associated with a game.

        Args:
            game: The name of the game in kebab case.
        """

        return self.entity[game][str(_KEY.CHANNEL)]

    def role_ids(self) -> list[int]:
        """Returns all role IDs associated with a game."""

        return [
            values[str(_KEY.ROLE)]
            for values in self.entity.values()
        ]

    def channel_ids(self) -> list[int]:
        """Returns all channel IDs associated with a game."""

        return [
            values[str(_KEY.CHANNEL)]
            for values in self.entity.values()
        ]

    def game(self, id_: int) -> str:
        """Returns the name of a game in kebab case from a role or channel ID.

        Args:
            id_: The role or channel ID associated with a game.
        """

        for game, values in self.entity.items():
            if id_ in values.values():
                return game
