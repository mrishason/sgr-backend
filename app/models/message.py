from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Text
from ..database import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "message"
    MessageID = Column(Integer, primary_key=True, index=True)
    PassengerID = Column(Integer, ForeignKey("passenger.PassengerID"))
    ConversationID = Column(Integer, ForeignKey("conversation.ConversationID"))
    IntentID = Column(Integer, ForeignKey("intent.IntentID"), nullable=True)
    Text = Column(Text)
    Direction = Column(String)
    Type = Column(String)
    Timestamp = Column(DateTime)