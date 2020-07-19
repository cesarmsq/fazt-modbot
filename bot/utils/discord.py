import re
from typing import List

from discord import Member, Message, NotFound, utils
from discord.ext.commands import BadArgument, Bot, Converter, IDConverter

from .. import crud


def get_prefix(_: Bot, msg: Message) -> List[str]:
    guild = crud.get_guild(msg.guild.id)
    prefix_setting = crud.get_guild_setting(guild, "prefix")

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


to_minutes = {"d": 60 * 24, "h": 60, "m": 1, "s": 1 / 60}


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
