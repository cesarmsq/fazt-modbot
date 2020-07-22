"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from discord import Color, Embed, TextChannel
from discord.ext.commands import Bot, Cog, Context, group, has_permissions

from .. import crud

settings = {"moderation": "moderation_logs_channel", "rules": "rules_channel"}


class ServerConfigCmds(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx: Context):
        return ("manage_guild", True) in ctx.author.permissions_in(ctx.channel)

    #
    # Set
    #

    @group(
        help="Coloca canales y configuraciones. Canales para colocar: "
        + " ".join(settings.keys())
    )
    async def set(self, ctx: Context):
        pass

    @set.command(name="channel", invoke_without_command=True)
    async def set_channel(self, ctx: Context, setting, channel: TextChannel):
        if setting not in settings:
            return

        crud.set_guild_setting(ctx.guild.id, settings[setting], str(channel.id))

        embed = Embed(
            title="Canal colocado! ✅",
            description="El canal ha sido colocado.",
            color=Color.red(),
        )

        await ctx.send(embed=embed)

    @set.command(
        help="Muestra el prefix del bot o lo cambia, puedes cambiarlo a múltiples prefixes pasando varios argumentos "
        "separados por un espacio",
        usage="[nuevos prefixes separados por un espacio]",
    )
    @has_permissions(manage_guild=True)
    async def prefix(self, ctx: Context, *, new_prefixes: str = ""):
        def format_prefixes(p):
            p = p.split()
            return "`" + "`, `".join(p) + "`"

        if new_prefixes:
            crud.set_guild_setting(ctx.guild.id, "prefix", new_prefixes)
            embed = Embed(
                title="Prefix editado! ✅",
                description=f"Los prefixes ahora son: {format_prefixes(new_prefixes)}",
                color=Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            guild = crud.get_guild(ctx.guild.id)
            prefixes = crud.get_guild_setting(guild, "prefix")
            embed = Embed(
                title="Prefix del Bot",
                description=f"Los prefixes actuales son: {format_prefixes(prefixes)}",
                color=Color.red(),
            )
            await ctx.send(embed=embed)

    #
    # Remove
    #

    @group(help="")
    async def remove(self, ctx: Context):
        pass

    @remove.command(name="channel")
    async def remove_channel(self, ctx: Context, name: str):
        if name not in settings:
            return

        crud.set_guild_setting(ctx.guild.id, settings[name], "")

        embed = Embed(
            title="Configuración eliminada! ✅",
            description="La configuración ha sido eliminada correctamente.",
            color=Color.red(),
        )

        await ctx.send(embed=embed)
