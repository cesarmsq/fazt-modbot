from discord import Message
from discord.ext.commands import Bot, Context

from .database import session
from .utils import get_prefix

bot = Bot(command_prefix=get_prefix)
bot.remove_command("help")


@bot.check
async def block_dms(ctx: Context) -> bool:
    return ctx.guild is not None


@bot.event
async def on_message(msg: Message) -> None:
    session()
    await bot.process_commands(msg)
    session.remove()


bot.load_extension("bot.cogs")
bot.load_extension("bot.commands")
