"""Handles everything related to the ticket data file.

Adapted from data.py written by Pwnion.
The ticket data file is a JSON file that stores the names of the ticket
modules as well as their filepaths and category IDs.
"""
import json

BASE_PATH = './cog/ticket/'
MODULE_FILE = 'ticket_data.json'
EMBED_FILE = 'embeds.json'

class Singleton(type):
    """A singleton metaclass."""

    instance = None

    def __call__(cls, *args, **kw) -> None:
        if not cls.instance:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)

        return cls.instance


class Ticket_Data(metaclass=Singleton):
    """Handles the persistent data in the data file.

    Provides I/O methods for the data file and parses
    the data to provide convenient attributes and methods
    for accessing the data in common ways.
    """

    def __init__(self) -> None:
        # Load the data file as a dictionary.
        with open(BASE_PATH + MODULE_FILE, 'r') as file:
            self._modules = json.load(file)
            
        with open(BASE_PATH + EMBED_FILE, 'r') as file:
            self._embed = json.load(file)
            
    def module_names(self) -> list:
        """Return a list of all ticket modules"""
        
        return [self._modules[module] for module in self._modules.keys()]
            
    def module(self, name:str) -> dict:
        """Returns the supplied information on a ticket module
        
        Args:
            name: name of the ticket module
        """
        return self._modules[name]
            
    def embed(self, name: str) -> dict:
        """Returns an embed by name supplied in _embeds
        
        Args:
            name: name of the embed required
        """
        return self._embed[name]