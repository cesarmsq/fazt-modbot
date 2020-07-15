from typing import Optional, Union, List

import discord
from discord.ext import commands

from .. import crud
from ..models import Moderation


class UserCmds(commands.Cog, name='Comandos para el usuario'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(help='Muestra ayuda acerca del bot', aliases=['ayuda', 'comandos', 'commands'], usage='[comando]')
    async def help(self, ctx: commands.Context, *, command_name: str = ''):
        no_description_msg = '(Sin descripción)'

        def display_info(cmd: commands.Command, simple=False):
            command_description = ''

            if simple:
                command_description += f'`{cmd.name}`: '
                command_description += cmd.help or no_description_msg
                command_description += '\n'
                return command_description

            if cmd.usage:
                command_description += f'\nUso: `{ctx.prefix}{cmd.name} {cmd.usage}`'

            if cmd.aliases:
                aliases_list = "`, `".join(cmd.aliases)
                command_description = f'\nAlias: `{aliases_list}`'

            group_commands = getattr(cmd, 'commands', None)

            if group_commands:
                command_description += '\n\n**Commands:**\n'
                for group_command in group_commands:
                    command_description += display_info(group_command, simple=True)

            return command_description

        if command_name:
            command = self.bot.get_command(command_name)
            if command is None:
                embed = discord.Embed(
                    title=f'El comando {command_name} no existe',
                    description=f'Usa `{ctx.prefix}help` para obtener una lista sobre los comandos.',
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title=f'Ayuda sobre el comando {command.name}',
                    description=command.help or no_description_msg,
                    color=discord.Color.red()
                )
                embed.description += display_info(command)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title='Ayuda',
                description=f'Prefix: `{ctx.prefix}`',
                color=discord.Color.red()
            )

            embed.description += f'\nUsa `{ctx.prefix}{ctx.command} <comando>` para obtener más ' \
                                 f'información sobre un comando específico.\nLista de comandos del bot:'

            for cog_name, cog in self.bot.cogs.items():
                cog_commands = cog.get_commands()
                if not cog_commands:
                    continue

                value = ''
                for command in cog_commands:
                    value += display_info(command, simple=True)
                embed.add_field(name=cog.qualified_name or cog_name, value=value, inline=False)

            await ctx.send(embed=embed)

    def show_history(
            self, moderation: List[Moderation], embed: discord.Embed, include_type=True, page: Optional[int] = None
    ):
        embed.description += '\n'

        plus = 0
        if page:
            plus = (page - 1) * 10

        has_history = False
        for index, moderation in enumerate(moderation):
            has_history = True
            embed.description += f'\n`{index + 1 + plus}` '

            if include_type:
                embed.description += f'[{moderation.type.title()}] '

            reason = moderation.reason or 'Sin razón'
            embed.description += f'**{reason}** '

            moderator_id = moderation.moderator_id
            moderator = None

            if moderator_id:
                channel: discord.TextChannel
                moderator = discord.utils.get(self.bot.users, id=int(moderator_id))

            if moderator:
                embed.description += f'por {moderator.mention}'

            embed.description += 'en `' + moderation.creation_date.strftime('%a %d, %Y') + '`'

        return has_history

    @staticmethod
    async def can_see_history(ctx: commands.Context, member: Optional[discord.Member]):
        if not ctx.author.top_role:
            return False

        contributors = discord.utils.get(ctx.guild.roles, name='Contributors')

        if contributors is None:
            await ctx.send('No has creado el rol Contributors, por favor crealo.')
            return False

        if member and (not isinstance(member, int)) and (not ctx.author.top_role >= contributors):
            await ctx.send('No puedes ver el historial de este usuario.')
            return False

        return True

    @commands.command()
    async def history(
            self, ctx: commands.Context, member_or_page: Union[discord.Member, int] = 1, page: int = 1
    ):
        if not await self.can_see_history(ctx, member_or_page):
            return

        member = member_or_page
        if isinstance(member, int):
            page = member_or_page
            member = ctx.author

        history, total_pages = crud.get_all_moderations(ctx.guild.id, member.id, page=page)

        embed = discord.Embed(
            title=f'Historial de moderación',
            description=f'Historial de {member.mention}',
            color=discord.Color.red()
        )

        has_history = self.show_history(history, embed, page=page)
        if has_history:
            embed.set_footer(text=f'Página {page} de {total_pages}')
        else:
            message = 'No existe esta página.'
            if page == 1:
                message = 'El usuario no tiene moderaciones.'

            embed.description += message

        await ctx.send(embed=embed)

    @commands.command()
    async def warninfo(self, ctx: commands.Context, member: discord.Member):
        if not await self.can_see_history(ctx, member):
            return

        if member is None:
            member = ctx.author

        warnings = crud.get_moderations('advertido', member.id, ctx.guild.id)

        embed = discord.Embed(
            title=f'Historial de warnings',
            description=f'Warnings de {member.mention}',
            color=discord.Color.red()
        )

        self.show_history(warnings, embed, include_type=False)
        await ctx.send(embed=embed)
