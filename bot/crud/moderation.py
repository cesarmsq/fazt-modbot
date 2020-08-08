"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from datetime import datetime
from typing import Optional

from ..database import session
from ..enums import ModerationType
from ..models import Moderation
from . import create_one, paginate


def moderate(
    moderation_type: ModerationType,
    user_id: int,
    date: datetime,
    expiration_date: Optional[datetime],
    guild_id: int,
    moderator_id: int,
    reason: str = "",
) -> None:
    create_one(
        Moderation,
        type=moderation_type,
        user_id=user_id,
        moderator_id=moderator_id,
        reason=reason,
        creation_date=date,
        expiration_date=expiration_date,
        guild_id=guild_id,
    )


def get_moderation(moderation_type: ModerationType, user_id: int, guild_id: int):
    return (
        Moderation.query.filter_by(
            type=moderation_type, user_id=user_id, guild_id=guild_id
        )
        .order_by(Moderation.id.desc())
        .first()
    )


def get_moderations(
    moderation_type: ModerationType, user_id: int, guild_id: int, page: int = 1
):
    return paginate(
        Moderation.query.filter_by(
            type=moderation_type, user_id=user_id, guild_id=guild_id
        ).order_by(Moderation.id.desc()),
        page=page,
        per_page=10,
    ).all()


def get_all_moderations(
    guild_id: int,
    user_id: Optional[int] = None,
    revoked: Optional[bool] = None,
    page: int = 1,
):
    query = Moderation.query.filter_by(guild_id=guild_id)

    if user_id:
        query = query.filter_by(user_id=user_id)

    if revoked is not None:
        query = query.filter(
            Moderation.revoked == revoked, Moderation.expiration_date.isnot(None)
        )

    query, total_pages = paginate(
        query.order_by(Moderation.id.desc()), page=page, per_page=10, include_total=True
    )

    return query.all(), total_pages


def revoke_moderation(moderation: Moderation):
    moderation.revoked = True
    session.commit()
