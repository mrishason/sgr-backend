from sqlalchemy import Column, Integer, String, DateTime
from ..database import Base
from datetime import datetime

class Passenger(Base):
    __tablename__ = "passenger"
    PassengerID = Column(Integer, primary_key=True, index=True)
    Name = Column(String)
    PhoneNumber = Column(String)
    Email = Column(String)
    PreferredLanguage = Column(String)
    PreferredChannel = Column(String)
    CreationDate = Column(DateTime, default=datetime.utcnow)
