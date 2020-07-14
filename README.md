# Fazt-ModBot

Discord bot with moderation commands for the fazt community.

## Setup/Usage

### Requirements

- Python version 3.7 or higher
- Pip

Install the pip requirements with `pip install -r requirements.txt`

### Required environment variables

Create a `.env` file in the same folder where the `bot` folder is located and add these lines:

```
DISCORD_TOKEN={Your bot's discord token here}
DATABASE_URL={your database's URL}
DEFAULT_SETTINGS={"prefix": "!", "debug": false}
DEVELOPERS_ID=[123, 456]
```

`DEVELOPERS_ID` is a json list of the discord id of each developer who has access to commands like `!reload` and `!debug` as an integer.

Replace the text between the brackets with the actual tokens, you have to get those from [discord](https://discordapp.com/developers/applications/) and from [google](https://console.developers.google.com/).

Alternatively, add the environment variables with `export` from your terminal (If you are on Windows, use `set` instead).

### Creating the databases

Create the database using `alembic upgrade head`

### Running the bot

To start the bot use `python -m bot`
