"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from .config import Settings
from .main import bot

bot.run(Settings.DISCORD_TOKEN)
