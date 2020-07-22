"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from typing import List, Optional, Union

from discord import Embed, Member, TextChannel, utils
from discord.ext.commands import Bot, CheckFailure, Context

from ..models import Moderation
from . import MentionedMember


def show_history(
    bot: Bot,
    moderation: List[Moderation],
    embed: Embed,
    include_type=True,
    page: Optional[int] = None,
) -> bool:
    embed.description += "\n"

    plus = 0
    if page:
        plus = (page - 1) * 10

    has_history = False
    for index, moderation in enumerate(moderation):
        has_history = True
        embed.description += f"\n`{index + 1 + plus}` "

        if include_type:
            embed.description += f"[{moderation.type.title()}] "

        reason = moderation.reason or "Sin razón"
        embed.description += f"**{reason}**"

        moderator_id = moderation.moderator_id
        moderator = None

        if moderator_id:
            channel: TextChannel
            moderator = utils.get(bot.users, id=int(moderator_id))

        if moderator:
            embed.description += f" por {moderator.mention}"

        embed.description += (
            " el `" + moderation.creation_date.strftime("%a %d, %Y") + "`"
        )

    return has_history


async def can_see_history(
    ctx: Context, member: Union[MentionedMember, Member, int, None]
) -> None:
    if not ctx.author.top_role:
        raise CheckFailure

    contributors = utils.get(ctx.guild.roles, name="Contributors")

    if contributors is None:
        await ctx.send(
            "No has creado el rol Contributors, por favor crealo.", delete_after=10
        )
        raise CheckFailure

    if (
        member
        and (not isinstance(member, int))
        and (not ctx.author.top_role >= contributors)
    ):
        await ctx.send("No puedes ver el historial de este usuario.", delete_after=10)
        raise CheckFailure
