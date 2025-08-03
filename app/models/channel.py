from sqlalchemy import Column, Integer, String, DateTime, JSON
from ..database import Base
from datetime import datetime

class Channel(Base):
    __tablename__ = "channel"
    ChannelID = Column(Integer, primary_key=True, index=True)
    Name = Column(String)
    Status = Column(String)
    ConfigDetails = Column(JSON)
    LastUpdated = Column(DateTime, default=datetime.utcnow)
