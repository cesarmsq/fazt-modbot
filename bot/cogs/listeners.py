import logging
from asyncio import create_task
from datetime import datetime

from discord import Color, Embed, Forbidden, Game, Guild, Member, NotFound, utils
from discord.ext.commands import (
    BadArgument,
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
from ..models import Moderation
from ..utils import callback as cb
from ..utils import to_bool, unmoderate


async def unban(guild: Guild, member: Member, member_id: int):
    if member:
        func = member.unban
    else:
        bans = await guild.bans()
        ban = utils.find(lambda b: b.user.id == member_id, bans)

        func = None
        if ban:
            func = cb(guild.unban, ban.user)

    await unmoderate(func, member_id, guild.id, "baneado")


async def unmute(guild: Guild, member: Member, __):
    if member:
        role = utils.get(guild.roles, name="Muted")
        func = cb(member.remove_roles, role)
        await unmoderate(func, member.id, guild.id, "silenciado")


async def revoke_moderation(guild: Guild, moderation: Moderation):
    if moderation.expiration_date > datetime.utcnow():
        await utils.sleep_until(moderation.expiration_date)

    map_moderations = {"silenciado": unmute, "baneado": unban}

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
    async def on_command_error(self, ctx: Context, error: CommandError):
        await ctx.message.delete()
        cmd = ctx.message.content.split()[0]
        embed = Embed(title="Error ❌", color=Color.red())

        original = getattr(error, "original", None)

        unknown_error_msg = "Error desconocido"
        forbidden_message = (
            "El bot no tiene permisos suficientes para realizar esa acción. ||"
            + getattr(original, "text", "")
            + "||"
        )
        no_permission_msg = "No tienes permisos suficientes para usar ese comando."

        errors = {
            ExpectedClosingQuoteError: "Te ha faltado cerrar una comilla.",
            BadArgument: "Has puesto mal algún argumento.",
            CommandError: "No tienes acceso a este comando.",
            CommandNotFound: f"El comando `{cmd}` no existe.\nPuedes utilizar `{ctx.prefix}help` para ver una lista detallada de los comandos disponibles.",
            CheckFailure: no_permission_msg,
            MissingPermissions: no_permission_msg,
            MissingRequiredArgument: f"Faltan argumentos. Revisa el `{ctx.prefix}help {ctx.command}` para obtener ayuda acerca del comando.",
            BotMissingPermissions: forbidden_message,
        }

        original_errors = {
            Forbidden: forbidden_message,
            NotFound: "404: No encontrado.",
        }

        original_type = type(original)
        message = errors.get(type(error), original_errors.get(original_type))

        embed.description = message

        if message is None:
            embed.description = unknown_error_msg
            guild = crud.get_guild(ctx.guild.id)
            setting = crud.get_guild_setting(guild, "debug")

            debug = False
            if setting and isinstance(setting, str):
                debug = to_bool(setting)

            if debug:
                error_msg = str(error)
                if error_msg:
                    embed.description += f":\n||```{error_msg}```||"
            logging.error(str(error), type(error), getattr(original, "text", ""))

        embed.description += "\nEste mensaje se eliminará luego de 30 segundos."

        await ctx.send(embed=embed, delete_after=30)
