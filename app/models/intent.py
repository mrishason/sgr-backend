from sqlalchemy import Column, Integer, String
from ..database import Base

class Intent(Base):
    __tablename__ = "intent"
    IntentID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, unique=True)
    Description = Column(String)
    ResponseTemplate = Column(String)
    Priority = Column(Integer)
