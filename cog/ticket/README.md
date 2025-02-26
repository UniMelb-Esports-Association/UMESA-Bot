## Overview
This cog handles all the ticketing functionality of the bot.
Currently, there are four ticket modules implemented.
*Note: Due to the constraints of discord.Modal (only 5 fields per Modal), only one more module can be added without changing the base code.*
## Prerequisites
[Discord.py](https://discordpy.readthedocs.io/en/stable/) version 2.4.0 is required for this cog to run.

## Files
There is 1 necessary file for this cog to function as found below:

- `ticket_data.json` contains the necessary roles and category specific information to determine channel creation and role permissions.
IDs for categories, roles and channels can be obtained by activating developer mode in Discord and right clicking the relevant object (see[ here](https://support-dev.discord.com/hc/en-us/articles/360028717192-Where-can-I-find-my-Application-Team-Server-ID)).
*Note: For modules with no embeds, ensure there is an empty list, []*
```
{
    "admin_role": <Role ID>,
    "clip": {
        "category_id: <Clips Category ID>,
        "embeds": {
            "description": "## Title",
            "color": 4638960,
            "image": {
            "url": "https://cdn.discordapp.com/attachments/1076108638755762246/1270728609002422302/team_1_logo.png?ex=66b4c1bd&is=66b3703d&hm=2312b4b1c04e834be2168bf581b0ee3746e218c6669249aadd46c43343d9c4fd&"
            },
            "description": "Some text goes here"
        }
    },
    "report": {
        "category_id": <Reports Category ID>,
        "embeds": []
    }
    ...
}
```


Ensure that `ticket_data.json` is located in the [same folder](./) as this file.