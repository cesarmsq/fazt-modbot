from .. import crud

from discord import Message
from discord.ext.commands import Bot, when_mentioned_or


def get_prefix(bot: Bot, msg: Message):
    guild = crud.get_guild(msg.guild.id)
    prefix_setting = crud.get_guild_setting(guild, 'prefix')
    prefixes = prefix_setting.split()
    return when_mentioned_or(*prefixes)(bot, msg)


async def unmoderate(
        func: callable, member_id: int, guild_id: int, moderation_type: str, expiration_needed: bool = True
):
    if func:
        moderation = crud.get_moderation(moderation_type, member_id, guild_id)

        if moderation.expired or not expiration_needed:
            await func()
            crud.revoke_moderation(moderation)
