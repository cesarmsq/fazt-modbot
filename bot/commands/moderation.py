from asyncio import create_task
from datetime import datetime, timedelta
from typing import Callable, Optional

from discord import Color, Embed, Forbidden, Member, PermissionOverwrite, utils
from discord.ext.commands import Bot, Cog, Context, Greedy, command, has_permissions

from .. import crud
from ..utils import Duration, MentionedMember
from ..utils import callback as cb
from ..utils import delete_message, get_value
from ..utils import unmoderate as unmod

no_logs_channel_msg = (
    "Usuario {title}. Considere agregar un canal para los logs usando `{prefix}set channel "
    "moderation #canal`. Este mensaje se eliminara en 10 segundos."
)

usage = "<usuarios> [duración] <razón>` Ejemplo de la duración: `1d5h3m10s` (1 dia, 5 horas, 3 minutos y 10 segundos)`"
usage2 = "<usuarios> <razón>"


async def unmoderate(ctx, title, member, after_duration, expiration_date):
    if expiration_date:
        await utils.sleep_until(expiration_date)
        await unmod(after_duration, member.id, ctx.guild.id, title)


class ModerationCmds(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx: Context):
        # TODO !!!!
        role = utils.get(ctx.guild.roles, name="Contributors")
        if role is None:
            create_task(
                ctx.send("No has creado el rol Contributors, por favor crealo.")
            )
            return False
        return ctx.author.top_role and ctx.author.top_role >= role

    async def moderate(
        self,
        ctx: Context,
        callback: Callable,
        title: str,
        reason: str,
        member: Member,
        emoji: str = "",
        duration: Optional[int] = None,
        after_duration: Callable = None,
    ):
        await delete_message(ctx.message)

        if member.top_role and not ctx.author.top_role > member.top_role:
            return await ctx.send(
                f"No puedes moderar a {member.display_name}.", delete_after=10
            )

        moderation_date = datetime.utcnow()

        expiration_date = None
        if duration and after_duration:
            expiration_date = moderation_date + timedelta(minutes=duration)

        value = get_value(reason, duration, expiration_date)

        try:
            await member.send(
                f"Has sido {title} en {ctx.guild.name}. Recuerda seguir las reglas!"
                + value
            )
        except Forbidden:
            await ctx.send(
                f"El usuario {member.display_name} tiene bloqueados los mensajes directos",
                delete_after=10,
            )

        await callback(reason=reason)
        crud.moderate(
            title,
            member.id,
            moderation_date,
            expiration_date,
            ctx.guild.id,
            ctx.author.id,
            reason or "",
        )

        guild = crud.get_guild(member.guild.id)
        channel = crud.get_set_channel(self.bot, guild, "moderation_logs_channel")

        if channel:
            embed = Embed(
                title=f"{emoji} Usuario {title}: {member.display_name}",
                description=f"El usuario {member.mention} ha sido {title} por {ctx.author.mention}\n"
                + value,
                color=Color.red(),
            )

            if expiration_date:
                embed.timestamp = expiration_date
                embed.set_footer(text="Expira:")

            message = member.mention
            rules_channel = crud.get_set_channel(self.bot, guild, "rules_channel")

            if rules_channel:
                message += " lee las reglas: " + rules_channel.mention

            await channel.send(message, embed=embed)

        else:
            await ctx.send(
                no_logs_channel_msg.format(title=title, prefix=ctx.prefix),
                delete_after=10,
            )

        create_task(unmoderate(ctx, title, member, after_duration, expiration_date))

    @command(help="Advierte a un usuario.", usage=usage2)
    async def warn(
        self, ctx: Context, members: Greedy[MentionedMember], *, reason: str
    ):
        role = utils.get(ctx.guild.roles, name="Warning")

        if role is None:
            role = await ctx.guild.create_role(
                name="Warning", color=Color.darker_grey()
            )

        for member in members:
            await self.moderate(
                ctx, cb(member.add_roles, role), "advertido", reason, member, "📢"
            )

    @command(
        help="Elimina los últimos <cantidad> mensajes o el último si ningún argumento es usado.",
        usage="[cantidad]",
    )
    @has_permissions(manage_messages=True)
    async def clear(self, ctx: Context, amount: int = 1):
        await ctx.channel.purge(limit=amount + 1)

        embed = Embed(
            title="Mensajes eliminados! ✅",
            description=f"{amount} mensajes han sido eliminados satisfactoriamente\nEste mensaje va a ser eliminado en 5 segundos",
            color=Color.red(),
        )

        await ctx.send(embed=embed, delete_after=5)

    @command(help="Prohibe un usuario en el servidor", usage=usage)
    @has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: Context,
        members: Greedy[MentionedMember],
        duration: Optional[Duration] = None,
        *,
        reason: str,
    ):
        for member in members:
            await self.moderate(
                ctx, member.ban, "baneado", reason, member, "🔨", duration, member.unban
            )

    @command(
        help="Expulsa a un usuario del servidor", usage=usage2, aliases=["expulsar"],
    )
    @has_permissions(kick_members=True)
    async def kick(
        self, ctx: Context, members: Greedy[MentionedMember], *, reason: str
    ):
        for member in members:
            await self.moderate(ctx, member.kick, "expulsado", reason, member, "⛔")

    @command(
        help="Evita que un usuario envie mensajes o entre a canales de voz", usage=usage
    )
    @has_permissions(manage_messages=True)
    async def mute(
        self,
        ctx: Context,
        members: Greedy[MentionedMember],
        duration: Optional[Duration] = None,
        *,
        reason: str,
    ):
        role = utils.get(ctx.guild.roles, name="Muted")

        if role is None:
            role = await ctx.guild.create_role(name="Muted", color=Color.dark_grey())

            overwrite = PermissionOverwrite(send_messages=False, speak=False)
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, overwrite=overwrite)

        for member in members:
            await self.moderate(
                ctx,
                cb(member.add_roles, role),
                "silenciado",
                reason,
                member,
                "🔇",
                duration,
                cb(member.remove_roles, role),
            )
