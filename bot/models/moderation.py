from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.hybrid import hybrid_property

from . import Base


class Moderation(Base):
    __tablename__ = "moderations"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    user_id = Column(BigInteger)
    reason = Column(String)
    moderator_id = Column(BigInteger)
    guild_id = Column(BigInteger, ForeignKey("guilds.id"))
    expiration_date = Column(DateTime)
    creation_date = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)

    @hybrid_property
    def expired(self) -> bool:
        if self.expiration_date is None:
            return False
        return datetime.utcnow() > self.expiration_date
