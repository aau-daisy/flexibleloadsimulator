from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship

from app.data.database import Base


class Timestamp(Base):
    __tablename__ = "timestamp"

    id = Column('id', Integer, primary_key=True, nullable=False, autoincrement=True)
    timestamp = Column('timestamp', DateTime, nullable=False, unique=True)

    # timestamp_id = relationship("de")

    def __init__(self):
        pass
