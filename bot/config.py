import json
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
    DEFAULT_SETTINGS = json.loads(os.environ["DEFAULT_SETTINGS"])
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///guilds.db")
    DEVELOPERS_ID = json.loads(os.environ.get("DEVELOPERS_ID", "[]"))
