from asyncio import create_task
from datetime import datetime, timedelta

from discord import Member, Forbidden, Embed, Color, PermissionOverwrite, utils
from discord.ext import commands

from .. import crud
from ..utils import callback as cb, unmoderate as unmod, MemberAndArgs, delete_message, parse_args, get_value


no_logs_channel_msg = 'Usuario {title}. Considere agregar un canal para los logs usando `{prefix}set channel ' \
                      'moderation #canal`. Este mensaje se eliminara en 10 segundos.'

usage = '<usuarios> [duración (minutos)] [razón]'


async def unmoderate(ctx, title, member, after_duration, expiration_date):
    if expiration_date:
        await utils.sleep_until(expiration_date)
        await unmod(after_duration, member.id, ctx.guild.id, title)


class ModerationCmds(commands.Cog, name='Moderación'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        # TODO !!!!
        role = utils.get(ctx.guild.roles, name='Contributors')
        if role is None:
            create_task(
                ctx.send('No has creado el rol Contributors, por favor crealo.')
            )
            return False
        return ctx.author.top_role and ctx.author.top_role >= role

    async def moderate(
            self,
            ctx: commands.Context,
            callback: callable,
            title: str,
            args: str,
            member: Member,
            after_duration: callable = None
    ):
        await delete_message(ctx.message)

        if member.top_role and not ctx.author.top_role > member.top_role:
            return await ctx.send(f'No puedes moderar a {member.display_name}.', delete_after=10)

        reason, duration = parse_args(args, after_duration)
        moderation_date = datetime.utcnow()

        expiration_date = None
        if duration and after_duration:
            expiration_date = moderation_date + timedelta(minutes=duration)

        value = get_value(reason, duration, expiration_date)

        dm = member.dm_channel
        if dm is None:
            dm = await member.create_dm()

        try:
            await dm.send(f'Has sido {title} en {ctx.guild.name}. Recuerda seguir las reglas!' + value)
        except Forbidden:
            await ctx.send(f'El usuario {member.display_name} tiene bloqueados los mensajes directos', delete_after=10)

        await callback(reason=reason)
        crud.moderate(title, member.id, moderation_date, expiration_date, ctx.guild.id, ctx.author.id, reason or '')

        guild = crud.get_guild(member.guild.id)
        channel = crud.get_set_channel(self.bot, guild, 'moderation_logs_channel')

        if channel:
            embed = Embed(
                title=f'Usuario {title}',
                description=f'El usuario {member.mention} ha sido {title} por {ctx.author.mention}' + value,
                color=Color.red()
            )

            message = member.mention
            rules_channel = crud.get_set_channel(self.bot, guild, 'rules_channel')

            if rules_channel:
                value = 'Lee las reglas: ' + rules_channel.mention
                embed.description += '\n' + value
                message += ' ' + value

            await channel.send(message, embed=embed)

        else:
            await ctx.send(no_logs_channel_msg.format(title=title, prefix=ctx.prefix), delete_after=10)

        create_task(unmoderate(ctx, title, member, after_duration, expiration_date))

    @commands.command(help='Advierte a un usuario.', usage='<usuario> [razón]')
    async def warn(self, ctx: commands.Context, *, members_and_reason: MemberAndArgs):
        members, reason = members_and_reason
        role = utils.get(ctx.guild.roles, name='Warning')

        if role is None:
            role = await ctx.guild.create_role(name='Warning', color=Color.darker_grey())

        for member in members:
            await self.moderate(ctx, cb(member.add_roles, role), 'advertido', reason, member)

    @commands.command(help='Elimina los últimos <cantidad> mensajes o el último si ningún argumento es usado.', usage='[cantidad]')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int = 1):
        await ctx.channel.purge(limit=amount+1)

        embed = Embed(
            title='Mensajes eliminados! ✅',
            description=f'{amount} mensajes han sido eliminados satisfactoriamente\nEste mensaje va a ser eliminado en 5 segundos',
            color=Color.red()
        )

        await ctx.send(embed=embed, delete_after=5)

    @commands.command(help='Prohibe un usuario en el servidor', usage=usage)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, *, members_and_reason: MemberAndArgs):
        members, args = members_and_reason

        for member in members:
            await self.moderate(ctx, member.ban, 'baneado', args, member, member.unban)

    @commands.command(help='Expulsa a un usuario del servidor', usage='<usuario> [razón]', aliases=['expulsar'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, *, members_and_reason: MemberAndArgs):
        members, args = members_and_reason

        for member in members:
            await self.moderate(ctx, member.kick, 'expulsado', args, member)

    @commands.command(help='Evita que un usuario envie mensajes o entre a canales de voz', usage=usage)
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx: commands.Context, *, members_and_reason: MemberAndArgs):
        members, args = members_and_reason
        role = utils.get(ctx.guild.roles, name='Muted')

        if role is None:
            role = await ctx.guild.create_role(name='Muted', color=Color.dark_grey())

            overwrite = PermissionOverwrite(send_messages=False, speak=False)
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, overwrite=overwrite)

        for member in members:
            await self.moderate(
                ctx, cb(member.add_roles, role), 'silenciado', args, member, cb(member.remove_roles, role)
            )
