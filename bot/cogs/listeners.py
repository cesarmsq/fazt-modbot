import logging
from datetime import datetime
from asyncio import create_task

import discord
from discord.ext import commands

from .. import crud
from ..utils import to_bool, unmoderate, callback as cb
from ..config import Settings
from ..models import Moderation
from ..database import session_factory


async def unban(guild: discord.Guild, member: discord.Member, reason: str, member_id: int):
    if member:
        func = member.unban
    else:
        bans = await guild.bans()
        ban = discord.utils.find(lambda b: b.user.id == member_id, bans)

        func = None
        if ban:
            func = cb(guild.unban, ban.user)

    await unmoderate(func, member_id, guild.id, 'baneado')


async def unmute(guild: discord.Guild, member: discord.Member, _, __):
    if member:
        role = discord.utils.get(guild.roles, name='Muted')
        func = cb(member.remove_roles, role)
        await unmoderate(func, member.id, guild.id, 'silenciado')


async def revoke_moderation(guild: discord.Guild, moderation: Moderation):
    if moderation.expiration_date > datetime.utcnow():
        await discord.utils.sleep_until(moderation.expiration_date)

    map_moderations = {
        'silenciado': unmute,
        'baneado': unban
    }

    func = map_moderations.get(moderation.type)
    member = guild.get_member(moderation.user_id)
    await func(guild, member, moderation.reason, moderation.user_id)
    db = session_factory()
    crud.revoke_moderation(moderation, db)
    db.close()


class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Game('prefix: ' + Settings.DEFAULT_SETTINGS['prefix'])
        await self.bot.change_presence(activity=activity)
        logging.info('Bot is ready')

        for guild in self.bot.guilds:
            moderations, _ = crud.get_all_moderations(guild.id, revoked=False)
            for moderation in moderations:
                create_task(revoke_moderation(guild, moderation))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        cmd = ctx.message.content.split()[0]
        embed = discord.Embed(
            title='Error ❌',
            color=discord.Color.red()
        )

        original = getattr(error, 'original', None)

        unknown_error_msg = 'Error desconocido'
        forbidden_message = 'El bot no tiene permisos suficientes para realizar esa acción. ||' + \
                            getattr(original, 'text', '') + '||'
        no_permission_msg = 'No tienes permisos suficientes para usar ese comando.'

        errors = {
            commands.ExpectedClosingQuoteError: 'Te ha faltado cerrar una comilla.',
            commands.BadArgument: 'Has puesto mal algún argumento.',
            commands.CommandError: 'No tienes acceso a este comando.',
            commands.CommandNotFound: f'El comando `{cmd}` no existe.\nPuedes utilizar `{ctx.prefix}help` para ver una lista detallada de los comandos disponibles.',
            commands.CheckFailure: no_permission_msg,
            commands.MissingPermissions: no_permission_msg,
            commands.MissingRequiredArgument: f'Faltan argumentos. Revisa el `{ctx.prefix}help {ctx.command}` para obtener ayuda acerca del comando.',
            commands.BotMissingPermissions: forbidden_message
        }

        original_errors = {
            discord.Forbidden: forbidden_message,
            discord.NotFound: '404: No encontrado.'
        }

        original_type = type(original)
        message = errors.get(type(error), original_errors.get(original_type))

        embed.description = message

        if message is None:
            embed.description = unknown_error_msg
            guild = crud.get_guild(ctx.guild.id)
            debug = to_bool(crud.get_guild_setting(guild, 'debug'))
            if debug:
                error_msg = str(error)
                if error_msg:
                    embed.description += f':\n||```{error_msg}```||'
            logging.error(str(error), type(error), getattr(original, 'text', ''))

        await ctx.send(embed=embed)
