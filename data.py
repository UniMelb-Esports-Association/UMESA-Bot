import json
from enum import Enum

JSON_FILE = 'data.json'
MISC_GAMES = 'misc-games'


class KEY(Enum):
    HUB_CHANNEL = 1
    GAMING_CATEGORY = 2
    LOG_CHANNEL = 3
    MODIFY_ROOM_CHANNEL = 4
    MODIFY_ROOM_COMMANDS_MSG = 5
    HUB_THREAD = 6
    FORUM_CHANNEL = 7
    ROLE = 8
    ENTITY = 9

    def __str__(self):
        return self.name.lower()


class Singleton(type):
    instance = None

    def __call__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)

        return cls.instance


class Data(metaclass=Singleton):
    def __init__(self):
        with open(JSON_FILE, 'r') as file:
            self._data = json.load(file)

        for key, value in self._data.items():
            self.__setattr__(
                key + f'{"_id" if key != str(KEY.ENTITY) else ""}',
                value
            )

    @staticmethod
    def _kebab(str_: str):
        return str_.replace(' ', '-').lower()

    def add_game(
        self,
        name: str,
        hub_thread_id: int,
        forum_channel_id: int,
        role_id: int
    ) -> None:
        self.entity[self._kebab(name)] = {
            str(KEY.HUB_THREAD): hub_thread_id,
            str(KEY.FORUM_CHANNEL): forum_channel_id,
            str(KEY.ROLE): role_id,
        }

        with open(JSON_FILE, 'w') as file:
            json.dump(self._data, file, indent=4)

    def delete_game(self, name: str) -> None:
        del self.entity[self._kebab(name)]

        with open(JSON_FILE, 'w') as file:
            json.dump(self._data, file, indent=4)

    def thread_id(self, game: str) -> int:
        return self.entity[game][str(KEY.HUB_THREAD)]

    def forum_id(self, game: str) -> int:
        return self.entity[game][str(KEY.FORUM_CHANNEL)]

    def role_id(self, game: str) -> int:
        return self.entity[game][str(KEY.ROLE)]

    def thread_ids(self) -> list[int]:
        """Get all hub threads."""

        return [
            values[str(KEY.HUB_THREAD)]
            for values in self.entity.values()
        ]

    def forum_ids(self) -> list[int]:
        """Get all forums."""

        return [
            values[str(KEY.FORUM_CHANNEL)]
            for values in self.entity.values()
        ]

    def role_ids(self) -> list[int]:
        """Get all roles."""

        return [
            values[str(KEY.ROLE)]
            for values in self.entity.values()
        ]

    def game(self, id_: int) -> str:
        """Get the game from a hub thread id, game forum id or game role id."""

        for game, values in self.entity.items():
            if id_ in values.values():
                return game
