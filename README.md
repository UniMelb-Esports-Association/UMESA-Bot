## Overview
The UMESA Discord bot only runs in the official [UMESA Discord server](https://discord.gg/VvXuE2NGX6) and handles all functionality required by the server. It is written in Python and uses the [discord.py](https://discordpy.readthedocs.io/en/stable/) library.

## Setting up the Bot
*Note: All commands are for Debian Linux.*<br><br>

To setup the bot
1. Install Python 3.10+, the pip Python package manager and the Python virtual environment module.
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 -V # Check you have the correct version
```

2. Clone the [Github repository](https://github.com/UniMelb-Esports-Association/UMESA-Bot).
```bash
git clone https://github.com/UniMelb-Esports-Association/UMESA-Bot.git
```

3. Navigate to the cloned directory.
```bash
cd UMESA-Bot
```

4. Create a Python virtual environment called "venv".
```bash
python3 -m venv venv
```

5. Activate the virtual environment. (Note: Every time you run the bot you'll need to make sure you're inside the virtual environment by running this command. You can confirm it was successful by noticing your terminal prefix has changed to "venv")
```bash
source venv/bin/activate
```

6. Install dependencies into the virtual environment.
```bash
pip3 install discord.py python-dotenv
```

7. Create a .env file that contains the bot's token and a data.json file that contains the data required for the bot to work. See below for the format of these files.

8. Run the bot.
```bash
python3 main.py
```

## Files
As mentioned earlier, there are two files that the bot requires to function properly. Both should be located in the root of the project directory. They are listed here with a template below each one that conveys how each file should be structured and what data should be in them.

- `.env`
```
 DISCORD_TOKEN=<Discord Bot Token>
```

- `data.json`
```
{
    "gaming-category": <Gaming Category ID>,
    "team-category": <Team Category ID>,
    "log-channel": <Log Channel ID>,
    "modify-room-channel": <Modify Room Channel ID>,
    "entity": {}
}
```

## Contributing
The code uses the [discord.py](https://discordpy.readthedocs.io/en/stable/) library for interacting with the Discord backend in Python. You can find the API docs [here](https://discordpy.readthedocs.io/en/stable/api.html). The code also follows strict standards for structure, formatting and documentation. You must adhere to these standards for a pull request to be accepted.

### Structure
The [`main.py`](https://github.com/UniMelb-Esports-Association/UMESA-Bot/blob/main/main.py) file is the entry point for the program. It configures the bot, loads the `Bot` cog in [`bot.py`](https://github.com/UniMelb-Esports-Association/UMESA-Bot/blob/main/cog/bot.py) and then runs the bot.

#### Cogs
A cog can be thought of as a module for the bot, and each cog has a specific purpose. Each cog is contained within its own file, and all cog files are located in the [`/cog`](https://github.com/UniMelb-Esports-Association/UMESA-Bot/tree/main/cog) directory. A cog is represented by a class that inherits from [`discord.ext.commands.Cog`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?cog#discord.ext.commands.Cog). A truncated example of a cog is below.

```python
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot

    # The actual code for the cog goes here...

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ExampleCog(bot))
```

In this example, the `ExampleCog` class is the cog. It accepts a parameter of type [`Bot`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?bot#bot) to its constructor which represents the bot itself. The `setup` function is a hook used by [`discord.py`](https://discordpy.readthedocs.io/en/stable/index.html) to register the cog with the bot. All cogs follow this structure.

#### The `Bot` Cog
The `Bot` cog in [`bot.py`](https://github.com/UniMelb-Esports-Association/UMESA-Bot/blob/main/cog/bot.py) is loaded by [`main.py`](https://github.com/UniMelb-Esports-Association/UMESA-Bot/blob/main/main.py) and is the first cog to be loaded. The job of the `Bot` cog is mainly to load all other cogs and to [sync](https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.app_commands.CommandTree.sync) the [command tree](https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.app_commands.CommandTree), which registers all slash commands with every guild (the technical term for a server) that the bot is in. It is worth noting that the official UMESA Discord server is the only guild the bot is run in, which is also why we retrieve the first element of the [`discord.ext.commands.Bot.guilds`](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?bot#discord.ext.commands.Bot.guilds) list often throughout the code to get the object that represents the UMESA server.

#### Making Additions
Adding to the bot's code will either consist of editing an already existing cog or creating a new one. If the feature you are adding fits into the job of an already existing cog, then you can add the functionality to that. There are some extra steps if you are creating a new cog.

##### Steps for Creating a New Cog
1. Create a new file under the [`/cog`](https://github.com/UniMelb-Esports-Association/UMESA-Bot/tree/main/cog) directory. It's name must match the name of the cog class inside the file, but the case should not match as files use `snake_case` and classes use `CamelCase`.
2. Follow the aforementioned cog structure to write the code for a new cog in this newly created file.
3. Add your cog to the `_COGS` constant in the [`bot.py`](https://github.com/UniMelb-Esports-Association/UMESA-Bot/blob/main/cog/bot.py) file by adding the path to the cog's file relative to the [`/cog`](https://github.com/UniMelb-Esports-Association/UMESA-Bot/tree/main/cog) folder, using a '.' as the path separator.

### Formatting and Documentation
Consistently good formatting and documentation is essential for code readability and maintability. This applies all the way down to the level of correct punctuation in comments, for example. All code should follow [Google's Python Style Guide](https://google.github.io/styleguide/pyguide.html), but it is a long document so the most important parts of the document are linked below.

- [Exceptions](https://google.github.io/styleguide/pyguide.html#24-exceptions)
- [Type Hinting](https://google.github.io/styleguide/pyguide.html#221-type-annotated-code)
- [Line Length](https://google.github.io/styleguide/pyguide.html#3-python-style-rules)
- [Parentheses](https://google.github.io/styleguide/pyguide.html#33-parentheses)
- [Indentation](https://google.github.io/styleguide/pyguide.html#34-indentation)
- [Comments and Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Strings](https://google.github.io/styleguide/pyguide.html#310-strings)
- [Naming Conventions](https://google.github.io/styleguide/pyguide.html#3164-guidelines-derived-from-guidos-recommendations)
- [Line Breaking](https://google.github.io/styleguide/pyguide.html#3192-line-breaking)
- [Default Values](https://google.github.io/styleguide/pyguide.html#3194-default-values)

Notably we ignore [Google's Python Style Guide](https://google.github.io/styleguide/pyguide.html) for import statements. Instead, just group related imports together with a line break in between groups, and have lines that start with `import` before lines the start with `from` within each group. If you're unsure of anything, look at the existing code or ask the technical head.

### Testing
We have no good way of testing code currently. For now, leave the testing up to the technical head. In the future we may implement sharding so that multiple instances of the bot can run at once, and also add the bot to a testing server.

### Adding your Code to GitHub
To eventually get your code into the `main` branch, you should follow some simple steps.

1. Create a branch with a name that explains what feature you are working on.
2. Write and add your code to that branch.
3. Push your branch with the completed code to GitHub.
4. Create a pull request to the main branch.
5. Wait for an administrator to either approve or deny your pull request.
    - If approved, great job! You've successfully made a contribution.
    - If denied, read the comment explaining why it was denied and have a discussion with the person who denied it if you need further clarification. Engage in a cycle of fixing your code and resubmitting your pull request until it is approved.
