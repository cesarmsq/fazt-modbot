"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from typing import Optional, Union

from discord import TextChannel
from discord.ext.commands import Bot

from ..config import Settings
from ..database import session
from ..enums import GuildSetting
from ..models import Guild, Setting
from . import get_guild


def create_guild_setting(
    guild: Guild, setting_name: GuildSetting, setting_value: str
) -> None:
    setting = Setting(name=setting_name, value=setting_value, guild=guild)
    session.add(setting)
    session.commit()


def get_guild_setting(
    guild: Guild, setting_name: GuildSetting, as_db=False
) -> Union[Setting, str, None]:
    setting = Setting.query.filter(
        Setting.guild == guild, Setting.name == setting_name
    ).first()
    if as_db:
        return setting
    elif setting:
        return setting.value
    default = Settings.DEFAULT_SETTINGS.get(setting_name)
    return str(default) if default else None


def set_guild_setting(guild_id: int, setting_name: GuildSetting, setting_value: str):
    guild = get_guild(guild_id)
    setting = get_guild_setting(guild, setting_name, as_db=True)
    if setting and isinstance(setting, Setting):
        setting.value = setting_value
        session.commit()
    else:
        create_guild_setting(guild, setting_name, setting_value)
    return setting


def get_set_channel(
    bot: Bot, guild: Guild, setting_name: GuildSetting
) -> Optional[TextChannel]:
    channel_id = get_guild_setting(guild, setting_name)

    channel = None
    if channel_id and channel_id.isdigit():
        channel = bot.get_channel(int(channel_id))

    return channel
