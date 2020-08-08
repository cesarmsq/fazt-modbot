"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from math import ceil

from sqlalchemy.orm import Query

from ..database import Base, session


def find(model: Base, **kwargs):
    if not kwargs:
        raise TypeError("You must provide at least one keyword argument")
    return model.query.filter_by(**kwargs).first()


def get(model: Base, obj_id: int):
    return model.query.get(obj_id)


def create_one(model: Base, **kwargs):
    obj = model(**kwargs)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


def get_or_create(model: Base, **kwargs):
    obj = find(model, **kwargs)
    if obj is None:
        obj = create_one(model, **kwargs)
    return obj


def paginate(query: Query, page: int, per_page: int, include_total=False):
    start = (page - 1) * per_page

    count = query.count()
    query = query.slice(start, start + per_page)

    if not include_total:
        return query

    return query, ceil(count / per_page)
