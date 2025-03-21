"""Handles everything related to the ticket data file.

Adapted from data.py written by Pwnion.
The ticket data file is a JSON file that stores the names of the ticket
modules as well as their filepaths and category IDs.
"""
import json

BASE_PATH = './cog/ticket/'
MODULE_FILE = 'ticket_data.json'

class Singleton(type):
    """A singleton metaclass."""

    instance = None

    def __call__(cls, *args, **kw) -> None:
        if not cls.instance:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)

        return cls.instance


class TicketData(metaclass=Singleton):
    """Handles the persistent data in the data file.

    Provides I/O methods for the data file and parses
    the data to provide convenient attributes and methods
    for accessing the data in common ways.
    """

    def __init__(self) -> None:
        # Load the data file as a dictionary.
        with open(BASE_PATH + MODULE_FILE, 'r', encoding='utf-8') as file:
            self._modules = json.load(file)
            
    def module_names(self) -> list[str]:
        """Return a list of all ticket modules"""
        
        return list(self._modules.keys())
            
    def module(self, name:str) -> dict:
        """Returns the supplied information on a ticket module
        
        Args:
            name: name of the ticket module
        """
        return self._modules[name]