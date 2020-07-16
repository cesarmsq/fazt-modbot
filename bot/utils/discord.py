from .. import crud

from discord import Message, NotFound
from discord.ext.commands import Bot, BadArgument, MemberConverter, when_mentioned_or


def get_prefix(bot: Bot, msg: Message):
    guild = crud.get_guild(msg.guild.id)
    prefix_setting = crud.get_guild_setting(guild, 'prefix')
    prefixes = prefix_setting.split()
    return when_mentioned_or(*prefixes)(bot, msg)


async def delete_message(message):
    try:
        await message.delete()
    except NotFound:
        pass


class MemberAndArgs(MemberConverter):
    async def convert(self, ctx, argument):
        members = []
        args = []
        members_or_args = filter(bool, argument.split(' '))

        latest_was_arg = False
        for member_or_arg in members_or_args:
            if latest_was_arg:
                args.append(member_or_arg)
                continue

            try:
                member = await super().convert(ctx, member_or_arg)
            except BadArgument:
                latest_was_arg = True
                args.append(member_or_arg)
            else:
                members.append(member)

        if not members:
            raise BadArgument

        return members, ' '.join(args)
