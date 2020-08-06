"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from discord import Color, Embed
from discord.ext.commands import Bot, Cog, Context, command

from .. import crud
from ..config import Settings
from ..enums import GuildSetting
from ..utils import to_str_bool


class BotConfigCmds(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx: Context):
        return ctx.author.id in Settings.DEVELOPERS_ID

    @command()
    async def debug(self, ctx: Context, value: bool):
        crud.set_guild_setting(ctx.guild.id, GuildSetting.DEBUG, to_str_bool(value))
        embed = Embed(
            title="Debug configurado! ✅",
            description=f"Debug ha sido configurado como `{value}`",
            color=Color.red(),
        )
        await ctx.send(embed=embed)

    @command(help="Recarga el bot", usage="[extención]")
    async def reload(self, ctx: Context, *args: str):
        if args:
            for arg in args:
                self.bot.reload_extension(arg)
        else:
            self.bot.reload_extension("bot.cogs")
            self.bot.reload_extension("bot.commands")

        embed = Embed(
            title="Reloaded ✅",
            color=Color.red(),
            description="Bot recargado satisfactoriamente!",
        )

        await ctx.send(embed=embed)
