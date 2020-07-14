from . import Base

from sqlalchemy.orm import relationship
from sqlalchemy import BigInteger, Column


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    settings = relationship('Setting', backref='guild')
    moderations = relationship('Moderation')
