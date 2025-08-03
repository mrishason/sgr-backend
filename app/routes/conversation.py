from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Conversation, Passenger
from datetime import datetime

router = APIRouter()

@router.get("/conversations/")
def get_conversations(db: Session = Depends(get_db)):
    conversations = db.query(Conversation).all()
    result = []
    for convo in conversations:
        passenger = db.query(Passenger).filter_by(PassengerID=convo.PassengerID).first()
        result.append({
            "ConversationID": convo.ConversationID,
            "PassengerName": passenger.Name if passenger else "Unknown",
            "StartTime": convo.StartTime.strftime("%Y-%m-%d %H:%M")
        })
    return result

@router.delete("/conversations/{id}")
def delete_conversation(id: int, db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter_by(ConversationID=id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(convo)
    db.commit()
    return {"message": "Conversation deleted"}
