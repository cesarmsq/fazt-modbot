"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from typing import Callable

from discord import Color, Embed, Member, utils
from discord.ext.commands import Bot, Cog, Context, command, has_permissions

from .. import crud
from ..utils import callback as cb
from ..utils import unmoderate as unmod

no_logs_channel_msg = (
    "Usuario {title}. Considere agregar un canal para los logs usando `{prefix}set channel "
    "moderation #canal`. Este mensaje se eliminara en 10 segundos."
)

usage = "<usuario> [razón]"


class UnModerationCmds(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def unmoderate(
        self,
        ctx: Context,
        callback: Callable,
        title: str,
        moderation_type: str,
        reason: str,
        member: Member,
    ):
        await unmod(
            callback, member.id, ctx.guild.id, moderation_type, expiration_needed=False
        )
        await ctx.message.delete()

        guild = crud.get_guild(ctx.guild.id)
        channel = crud.get_set_channel(self.bot, guild, "moderation_logs_channel")

        if channel:
            embed = Embed(
                title=f"Usuario {title}",
                description=f"El usuario {member.mention} ha sido {title} por {ctx.author.mention}",
                color=Color.red(),
            )

            if reason:
                embed.description += f"\n**Razón**: {reason}"

            await channel.send(embed=embed)

        else:
            await ctx.send(
                no_logs_channel_msg.format(title=title, prefix=ctx.prefix),
                delete_after=10,
            )

    @command(
        help="Permite un usuario en el servidor que anteriormente habia sido baneado",
        usage=usage,
    )
    @has_permissions(ban_members=True)
    async def unban(self, ctx: Context, member_name: str, *, reason: str = ""):
        if member_name[0] == "@":
            member_name = member_name[1:]

        bans = await ctx.guild.bans()
        ban = utils.find(lambda b: b.user.name == member_name, bans)

        if ban is None:
            await ctx.send("No se encontró el ban")
            return

        user = ban.user

        await self.unmoderate(
            ctx, cb(ctx.guild.unban, user), "desbaneado", "baneado", reason, user
        )

    @command(
        help="Permite a un usuario silenciado hablar y escribir nuevamente", usage=usage
    )
    @has_permissions(manage_messages=True)
    async def unmute(self, ctx: Context, member: Member, *, reason: str = ""):
        role = utils.get(ctx.guild.roles, name="Muted")
        await self.unmoderate(
            ctx,
            cb(member.remove_roles, role),
            "des-silenciado",
            "silenciado",
            reason,
            member,
        )
