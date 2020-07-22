"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from sqlalchemy import BigInteger, Column
from sqlalchemy.orm import relationship

from . import Base


class Guild(Base):
    __tablename__ = "guilds"

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    settings = relationship("Setting", backref="guild")
    moderations = relationship("Moderation")
