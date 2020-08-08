"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from ..models import Guild
from . import get_or_create


def get_guild(guild_id):
    return get_or_create(Guild, id=guild_id)
