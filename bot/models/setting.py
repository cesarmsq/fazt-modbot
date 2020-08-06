"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from sqlalchemy import BigInteger, Column, Enum, ForeignKey, Integer, String

from ..database import Base
from ..enums import GuildSetting


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    name = Column(Enum(GuildSetting), nullable=False)
    value = Column(String(500), nullable=False)
    guild_id = Column(BigInteger, ForeignKey("guilds.id"))
