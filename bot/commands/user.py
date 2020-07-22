"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from typing import Union

from discord import Color, Embed, Member
from discord.ext.commands import Bot, Cog, Command, Context, command

from .. import crud
from ..utils import MentionedMember, can_see_history, show_history

no_description_msg = "(Sin descripción)"


def display_info(ctx: Context, cmd: Command, simple=False):
    command_description = ""

    if simple:
        command_description += f"`{cmd.name}`: "
        command_description += cmd.help or no_description_msg
        command_description += "\n"
        return command_description

    if cmd.usage:
        command_description += f"\nUso: `{ctx.prefix}{cmd.name} {cmd.usage}`"

    if cmd.aliases:
        aliases_list = "`, `".join(cmd.aliases)
        command_description += f"\nAlias: `{aliases_list}`"

    group_commands = getattr(cmd, "commands", None)

    if group_commands:
        command_description += "\n\n**Commands:**\n"
        for group_command in group_commands:
            command_description += display_info(ctx, group_command, simple=True)

    return command_description


class UserCmds(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(
        help="Muestra ayuda acerca del bot",
        aliases=["ayuda", "comandos", "commands"],
        usage="[comando]",
    )
    async def help(self, ctx: Context, *, command_name: str = ""):
        if command_name:
            cmd = self.bot.get_command(command_name)
            if cmd is None:
                embed = Embed(
                    title=f"El comando {command_name} no existe",
                    description=f"Usa `{ctx.prefix}help` para obtener una lista sobre los comandos.",
                    color=Color.red(),
                )
                await ctx.send(embed=embed)
            else:
                embed = Embed(
                    title=f"Ayuda sobre el comando {cmd.name}",
                    description=cmd.help or no_description_msg,
                    color=Color.red(),
                )
                embed.description += display_info(ctx, cmd)
                await ctx.send(embed=embed)
        else:
            embed = Embed(
                title="Ayuda", description=f"Prefix: `{ctx.prefix}`", color=Color.red()
            )

            embed.description += (
                f"\nUsa `{ctx.prefix}{ctx.command} <comando>` para obtener más "
                f"información sobre un comando específico.\nLista de comandos del bot:"
            )

            for cog_name, cog in self.bot.cogs.items():
                cog_commands = cog.get_commands()
                if not cog_commands:
                    continue

                value = ""
                for cmd in cog_commands:
                    value += display_info(ctx, cmd, simple=True)
                embed.add_field(
                    name=cog.qualified_name or cog_name, value=value, inline=False
                )

            await ctx.send(embed=embed)

    @command()
    async def history(
        self,
        ctx: Context,
        member_or_page: Union[MentionedMember, int, Member] = 1,
        page: int = 1,
    ):
        await can_see_history(ctx, member_or_page)

        member = member_or_page
        if isinstance(member, int):
            page = member_or_page
            member = ctx.author

        history, total_pages = crud.get_all_moderations(
            ctx.guild.id, member.id, page=page
        )

        embed = Embed(
            title="Historial de moderación",
            description=f"Historial de {member.mention}",
            color=Color.red(),
        )

        has_history = show_history(self.bot, history, embed, page=page)
        if has_history:
            embed.set_footer(text=f"Página {page} de {total_pages}")
        else:
            message = "No existe esta página."
            if page == 1:
                message = "El usuario no tiene moderaciones."

            embed.description += message

        await ctx.send(embed=embed)
