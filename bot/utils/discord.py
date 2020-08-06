"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""
import re
from typing import List, Optional

from discord import Guild, Member, Message, NotFound, Role, utils
from discord.ext.commands import BadArgument, Bot, Converter, IDConverter
from discord.ext.menus import Menu, button

from .. import crud
from ..enums import GuildSetting


def get_role(guild: Guild, role_type: GuildSetting) -> Optional[Role]:
    db_guild = crud.get_guild(guild.id)
    role_id = crud.get_guild_setting(db_guild, role_type)

    role: Optional[GuildSetting] = None
    if role_id and role_id.isdigit():
        role = utils.get(guild.roles, id=int(role_id))

    return role


def get_prefix(_: Bot, msg: Message) -> List[str]:
    guild = crud.get_guild(msg.guild.id)
    prefix_setting = crud.get_guild_setting(guild, GuildSetting.PREFIX)

    if isinstance(prefix_setting, str):
        prefixes = prefix_setting.split()
        return prefixes

    return ["!"]


async def delete_message(message: Message) -> None:
    try:
        await message.delete()
    except NotFound:
        pass


class MentionedMember(IDConverter):
    async def convert(self, ctx, argument: str) -> Member:
        result = None
        match = self._get_id_match(argument) or re.match(r"<@!?([0-9]+)>$", argument)

        if match:
            user_id = int(match.group(1))
            result = ctx.guild.get_member(user_id) or utils.get(
                ctx.message.mentions, id=user_id
            )

        if result is None:
            raise BadArgument('Member "{}" not found'.format(argument))

        return result


to_minutes = {"w": 60 * 24 * 7, "d": 60 * 24, "h": 60, "m": 1, "s": 1 / 60}


def parse_minutes(s: str) -> int:
    time = {"d": 0, "h": 0, "m": 0, "s": 0}

    current_time = ""
    for char in s:
        if char.isdigit():
            current_time += char
            continue

        time[char] += int(current_time)
        current_time = ""

    total = 0.0

    for k, v in time.items():
        total += v * to_minutes[k]

    if not total:
        return int(s)

    return int(total)


class Duration(Converter):
    async def convert(self, _, argument: str) -> int:
        try:
            result = parse_minutes(argument)
        except (KeyError, ValueError):
            raise BadArgument

        return result


class Confirm(Menu):
    def __init__(self, msg):
        super().__init__(timeout=30.0, delete_message_after=True)
        self.msg = msg
        self.result = None

    async def send_initial_message(self, ctx, channel):
        return await channel.send(self.msg)

    @button("\N{WHITE HEAVY CHECK MARK}")
    async def do_confirm(self, _):
        self.result = True
        self.stop()

    @button("\N{CROSS MARK}")
    async def do_deny(self, _):
        self.result = False
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait=True)
        return self.result
