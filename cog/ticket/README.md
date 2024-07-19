## Overview
This cog handles all the ticketing functionality of the bot.
Currently, there is only one ticket module implemented, however this cog can be extended by inheriting from the [ticketing.py](ticketing.py) class.
*Note: The ticket_data.json file can also be modified to support extensions.*

## Prerequisites
[Discord.py](https://discordpy.readthedocs.io/en/stable/) version 2.4.0 is required for this cog to run.

## Files
The file for this cog contains necessary, server specific information.
IDs for categories, roles and channels can be obtained by activating developer mode in Discord and right clicking the relevant object (see[ here](https://support-dev.discord.com/hc/en-us/articles/360028717192-Where-can-I-find-my-Application-Team-Server-ID)).
- `ticket_data.json`
```
{
    "clip": {
        "category_id: <Clips Category ID>",
        "role_id": <Role ID"
    }
}
```
Ensure that ticket_data.json is located in the [same folder](./) as this file