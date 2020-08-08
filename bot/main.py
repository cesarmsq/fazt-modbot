"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""
from discord.ext.commands import Context

from .bot import Bot
from .utils import get_prefix

bot = Bot(command_prefix=get_prefix)
bot.remove_command("help")


@bot.check
async def block_dms(ctx: Context) -> bool:
    return ctx.guild is not None


bot.load_extension("bot.cogs")
bot.load_extension("bot.commands")
