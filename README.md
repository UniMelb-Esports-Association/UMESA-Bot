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

5. Activate the virtual environment.
```bash
source venv/bin/activate
```

6. Install dependencies into the virtual environment (Note: Every time you run the bot you'll need to make sure you're inside the virtual environment by running this command. You can confirm it was successful by noticing your terminal prefix has changed to "venv").
```bash
pip3 install discord.py python-dotenv
```

7. Create a .env file that contains the bot's token and a data.json file that contains the data required for the bot to work. See below for the format of these files.

8. Run the bot.
```bash
python3 main.py
```

## Files
As mentioned earlier, there are two files that the bot requires to function properly. Both should be located in the root of the project directory. They are listed here with a template below each one that conveys how each file should be structured and what information should start in them.

- .env
```
 DISCORD_TOKEN=<Discord Bot Token>
 ```

- data.json
```
{
    "gaming-category": <Gaming Category ID>,
    "log-channel": <Log Channel ID>,
    "modify-room-channel": <Modify Room Channel ID>,
    "entity": {}
}
```

## Code Structure
