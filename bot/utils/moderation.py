"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from datetime import datetime
from typing import Callable, Optional

from .. import crud


def get_value(
    reason: str, duration: Optional[int], expiration_date: Optional[datetime]
) -> str:
    value = ""

    if reason:
        value += f"\n**Razón**: {reason}"

    if expiration_date:
        value += f"\n**Duración**: {duration} minutos"

    return value


async def unmoderate(
    func: Callable,
    member_id: int,
    guild_id: int,
    moderation_type: str,
    expiration_needed: bool = True,
) -> None:
    if func:
        moderation = crud.get_moderation(moderation_type, member_id, guild_id)

        if moderation.expired or not expiration_needed:
            await func()
            crud.revoke_moderation(moderation)
