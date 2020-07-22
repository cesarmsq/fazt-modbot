"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String

from . import Base


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    value = Column(String(500), nullable=False)
    guild_id = Column(BigInteger, ForeignKey("guilds.id"))
