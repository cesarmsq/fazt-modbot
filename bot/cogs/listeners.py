"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

import logging
from asyncio import create_task
from datetime import datetime

from discord import Color, Embed, Forbidden, Game, Guild, Member, NotFound, utils
from discord.ext.commands import (
    BadArgument,
    BadUnionArgument,
    Bot,
    BotMissingPermissions,
    CheckFailure,
    Cog,
    CommandError,
    CommandNotFound,
    Context,
    ExpectedClosingQuoteError,
    MissingPermissions,
    MissingRequiredArgument,
)

from .. import crud
from ..config import Settings
from ..database import session_factory
from ..enums import GuildSetting, ModerationType
from ..models import Moderation
from ..utils import callback as cb
from ..utils import get_role, to_bool, unmoderate


async def unban(guild: Guild, _: Member, member_id: int):
    bans = await guild.bans()
    ban = utils.find(lambda b: b.user.id == member_id, bans)

    func = None
    if ban:
        func = cb(guild.unban, ban.user)

    await unmoderate(func, member_id, guild.id, ModerationType.BAN)


async def unmute(guild: Guild, member: Member, __):
    if not member:
        return

    role = get_role(guild, GuildSetting.MUTED_ROLE)

    if not role:
        return

    func = cb(member.remove_roles, role)
    await unmoderate(func, member.id, guild.id, ModerationType.MUTE)


async def revoke_moderation(guild: Guild, moderation: Moderation):
    if moderation.expiration_date > datetime.utcnow():
        await utils.sleep_until(moderation.expiration_date)

    map_moderations = {ModerationType.MUTE: unmute, ModerationType.BAN: unban}

    member = guild.get_member(moderation.user_id)
    func = map_moderations.get(moderation.type)

    if func:
        await func(guild, member, moderation.user_id)
        db = session_factory()
        crud.revoke_moderation(moderation, db)
        db.close()


class Listeners(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        activity = Game("prefix: " + Settings.DEFAULT_SETTINGS["prefix"])
        await self.bot.change_presence(activity=activity)
        logging.info("Bot is ready")

        for guild in self.bot.guilds:
            moderations, _ = crud.get_all_moderations(guild.id, revoked=False)
            for moderation in moderations:
                create_task(revoke_moderation(guild, moderation))

    @Cog.listener()
    async def on_member_join(self, member: Member):
        guild = member.guild
        moderation = crud.get_moderation(ModerationType.MUTE, member.id, guild.id)

        if moderation and not (moderation.expired or moderation.revoked):
            role = get_role(guild, GuildSetting.MUTED_ROLE)
            await member.add_roles(role)

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: CommandError):
        await ctx.message.delete()
        cmd = ctx.message.content.split()[0]
        embed = Embed(title="Error ❌", color=Color.red())

        original = getattr(error, "original", None)

        forbidden_message = (
            "El bot no tiene permisos suficientes para realizar esa acción. ||"
            + getattr(original, "text", "")
            + "||"
        )
        no_permission_msg = "No tienes permisos suficientes para usar ese comando."

        bad_argument = "Has puesto mal algún argumento."

        errors = {
            ExpectedClosingQuoteError: "Te ha faltado cerrar una comilla.",
            BadArgument: bad_argument,
            CommandError: "No tienes acceso a este comando.",
            CommandNotFound: f"El comando `{cmd}` no existe.\nPuedes utilizar `{ctx.prefix}help` para ver una lista "
            f"detallada de los comandos disponibles.",
            CheckFailure: no_permission_msg,
            MissingPermissions: no_permission_msg,
            MissingRequiredArgument: f"Faltan argumentos. Revisa el `{ctx.prefix}help {ctx.command}` para obtener "
            f"ayuda acerca del comando.",
            BotMissingPermissions: forbidden_message,
            BadUnionArgument: bad_argument,
        }

        original_errors = {
            Forbidden: forbidden_message,
            NotFound: "404: No encontrado.",
        }

        original_type = type(original)
        message = errors.get(type(error), original_errors.get(original_type))

        embed.description = message

        if message is None:
            error_msg = str(error)
            logging.error(f"{type(error).__name__}: {error_msg}")

            embed.description = "Error desconocido"
            guild = crud.get_guild(ctx.guild.id)
            setting = crud.get_guild_setting(guild, GuildSetting.DEBUG)

            debug = False
            if setting and isinstance(setting, str):
                debug = to_bool(setting)

            if debug and error_msg:
                embed.description += f":\n||```{error_msg}```||"

        embed.description += "\nEste mensaje se eliminará luego de 30 segundos."

        await ctx.send(embed=embed, delete_after=30)
