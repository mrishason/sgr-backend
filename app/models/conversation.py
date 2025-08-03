from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from ..database import Base
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversation"
    ConversationID = Column(Integer, primary_key=True, index=True)
    PassengerID = Column(Integer, ForeignKey("passenger.PassengerID"))
    ChannelID = Column(Integer, ForeignKey("channel.ChannelID"))
    StartTimestamp = Column(DateTime, default=datetime.utcnow)
    EndTimestamp = Column(DateTime, nullable=True)
    Status = Column(String)
    AgentAssigned = Column(String)
    StartTime = Column(DateTime, default=datetime.utcnow)
