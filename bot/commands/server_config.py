"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""
from typing import List

from discord import Color, Embed, Role, TextChannel
from discord.ext.commands import Bot, Cog, Context, group, has_permissions

from .. import crud
from ..enums import GuildSetting
from ..utils import to_code_list_str

channel_settings = [GuildSetting.MODERATION_CHANNEL, GuildSetting.RULES_CHANNEL]

role_settings = [
    GuildSetting.MUTED_ROLE,
    GuildSetting.WARNING_ROLE,
    GuildSetting.MIN_MOD_ROLE,
]


def get_setting(name: str):
    for setting in GuildSetting:
        if setting.value == name:
            return setting
    return None


def format_settings(settings: List[GuildSetting]):
    settings = [setting.value for setting in settings]
    return to_code_list_str(settings)


class ServerConfigCmds(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx: Context):
        return ("manage_guild", True) in ctx.author.permissions_in(ctx.channel)

    #
    # Set
    #

    @group(
        help="Coloca canales y configuraciones.\n"
        f"Canales para colocar: {format_settings(channel_settings)}.\n"
        f"Roles para colocar: {format_settings(role_settings)}."
    )
    async def set(self, ctx: Context):
        pass

    @set.command(name="channel")
    async def set_channel(self, ctx: Context, setting, channel: TextChannel):
        setting = get_setting(setting)

        if not setting:
            return

        crud.set_guild_setting(ctx.guild.id, setting, str(channel.id))

        embed = Embed(title="Canal configurado!  ✅", color=Color.red(),)

        await ctx.send(embed=embed)

    @set.command(name="role")
    async def set_role(self, ctx: Context, role_type: str, role: Role):
        setting = get_setting(role_type)

        if not setting:
            return

        crud.set_guild_setting(ctx.guild.id, setting, str(role.id))

        embed = Embed(title="Rol configurado!  ✅", color=Color.red(),)

        await ctx.send(embed=embed)

    @set.command(
        help="Muestra el prefix del bot o lo cambia, puedes cambiarlo a múltiples prefixes pasando varios argumentos "
        "separados por un espacio",
        usage="[nuevos prefixes separados por un espacio]",
    )
    @has_permissions(manage_guild=True)
    async def prefix(self, ctx: Context, *, new_prefixes: str = ""):
        def format_prefixes(p):
            p = p or "!"
            return to_code_list_str(p.split())

        if new_prefixes:
            crud.set_guild_setting(ctx.guild.id, GuildSetting.PREFIX, new_prefixes)
            embed = Embed(
                title="Prefix editado! ✅",
                description=f"Los prefixes ahora son: {format_prefixes(new_prefixes)}",
                color=Color.red(),
            )
            await ctx.send(embed=embed)
        else:
            guild = crud.get_guild(ctx.guild.id)
            prefixes = crud.get_guild_setting(guild, GuildSetting.PREFIX)
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
        setting = get_setting(name)

        if not setting:
            return

        crud.set_guild_setting(ctx.guild.id, setting, "")

        embed = Embed(
            title="Configuración eliminada! ✅",
            description="La configuración ha sido eliminada correctamente.",
            color=Color.red(),
        )

        await ctx.send(embed=embed)
