from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, Base, engine
from . import models
from .models.message import Message
from .models.conversation import Conversation
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from app.database import get_db
from app.models.intent import Intent
from app.schemas import IntentCreate
from fastapi import Request
from app.nlp.trainer import IntentTrainer
from app.routes import whatsapp
from app.routes import conversation
from fastapi import UploadFile, File
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse
import io
from app.routes.nlp import classify_with_dialogflow
from app.nlp.trainer import IntentTrainer
from fastapi.responses import Response
from fastapi import Form

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(whatsapp.router)
app.include_router(conversation.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "SGR Chatbot API is running."}



# @app.post("/chat/")
# async def chat_endpoint(request: Request, db: Session = Depends(get_db)):
#     body = await request.json()
#     passenger_id = body.get("passenger_id")
#     message_text = body.get("message")

#     # 1. Tafuta au tengeneza conversation
#     conversation = db.query(Conversation).filter_by(PassengerID=passenger_id).first()
#     if not conversation:
#         conversation = Conversation(PassengerID=passenger_id, ChannelID=1, StartTime=datetime.now())
#         db.add(conversation)
#         db.commit()
#         db.refresh(conversation)

#     # 2. NLP Trainer
#     trainer = IntentTrainer(db)
#     result = trainer.predict(message_text)

#     if result:
#         intent_id = result["intent_id"]
#         response_text = result["response"]
#     else:
#         intent_id = None
#         response_text = "Samahani, sijaelewa swali lako."

#     # 3. Save messages
#     msg_in = Message(
#         PassengerID=passenger_id,
#         ConversationID=conversation.ConversationID,
#         IntentID=intent_id,
#         Text=message_text,
#         Direction="inbound",
#         Type="text",
#         Timestamp=datetime.now()
#     )
#     msg_out = Message(
#         PassengerID=passenger_id,
#         ConversationID=conversation.ConversationID,
#         IntentID=intent_id,
#         Text=response_text,
#         Direction="outbound",
#         Type="text",
#         Timestamp=datetime.now()
#     )
#     db.add_all([msg_in, msg_out])
#     db.commit()

#     return {"response": response_text}





@app.post("/chat/")
async def chat_endpoint(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    passenger_id = body.get("passenger_id")
    message_text = body.get("message")

    # 1. Get or create conversation
    conversation = db.query(Conversation).filter_by(PassengerID=passenger_id).first()
    if not conversation:
        conversation = Conversation(PassengerID=passenger_id, ChannelID=1, StartTime=datetime.now())
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    response_text = "Samahani, sijaelewa swali lako."
    intent_id = None

    # =========== STEP 1: Try Dialogflow ===========
    try:
        detected_intent, fulfillment_text = classify_with_dialogflow(message_text)

        if fulfillment_text:  # Dialogflow already gave a direct answer
            response_text = fulfillment_text
            # Try to map intent to DB (if exists)
            db_intent = db.query(Intent).filter(Intent.Name == detected_intent).first()
            if db_intent:
                intent_id = db_intent.IntentID

        else:
            raise ValueError("Hakuna fulfillmentText kutoka Dialogflow")

    except Exception as e:
        print("Dialogflow error:", e)

        # =========== STEP 2: Fallback to local NLP ===========
        trainer = IntentTrainer(db)
        local_result = trainer.predict(message_text)
        if local_result:
            response_text = local_result["response"]
            intent_id = local_result["intent_id"]

    # Save messages to DB
    msg_in = Message(
        PassengerID=passenger_id,
        ConversationID=conversation.ConversationID,
        IntentID=intent_id,
        Text=message_text,
        Direction="inbound",
        Type="text",
        Timestamp=datetime.now()
    )
    msg_out = Message(
        PassengerID=passenger_id,
        ConversationID=conversation.ConversationID,
        IntentID=intent_id,
        Text=response_text,
        Direction="outbound",
        Type="text",
        Timestamp=datetime.now()
    )
    db.add_all([msg_in, msg_out])
    db.commit()

    return {"response": response_text}
@app.get("/messages/")



def get_messages(db: Session = Depends(get_db)):
    return db.query(Message).all()

@app.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(Message).get(message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(msg)
    db.commit()
    return {"message": "Deleted"}

@app.get("/intent/")
def get_intents(db: Session = Depends(get_db)):
    return db.query(Intent).all()

@app.post("/intent/")
def create_intent(intent: IntentCreate, db: Session = Depends(get_db)):
    db_intent = Intent(**intent.dict())
    db.add(db_intent)
    db.commit()
    db.refresh(db_intent)
    return db_intent

@app.delete("/intent/{intent_id}")
def delete_intent(intent_id: int, db: Session = Depends(get_db)):
    intent = db.query(Intent).get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    db.delete(intent)
    db.commit()
    return {"message": "Intent deleted"}

@app.put("/intent/{intent_id}")
def update_intent(intent_id: int, intent: IntentCreate, db: Session = Depends(get_db)):
    db_intent = db.query(Intent).filter(Intent.IntentID == intent_id).first()
    if not db_intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    db_intent.Name = intent.Name
    db_intent.Description = intent.Description
    db_intent.ResponseTemplate = intent.ResponseTemplate
    db_intent.Priority = intent.Priority

    db.commit()
    db.refresh(db_intent)
    return db_intent

@app.delete("/intent/{intent_id}")
def delete_intent(intent_id: int, db: Session = Depends(get_db)):
    db_intent = db.query(Intent).filter(Intent.IntentID == intent_id).first()
    if not db_intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    
    db.delete(db_intent)
    db.commit()
    return {"message": "Intent deleted"}

@app.get("/conversations/")
def get_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).all()

@app.post("/intent/upload/")
async def upload_intents(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="File must be an Excel file")

    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))

    required_columns = {"Name", "Description", "ResponseTemplate", "Priority"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"Missing columns: {required_columns - set(df.columns)}")

    for _, row in df.iterrows():
        intent = Intent(
            Name=row["Name"],
            Description=row["Description"],
            ResponseTemplate=row["ResponseTemplate"],
            Priority=int(row["Priority"]),
        )
        db.add(intent)

    db.commit()
    return {"message": f"{len(df)} intents uploaded successfully"}


@app.get("/intent/template/")
def download_template():
    # Create a blank template
    df = pd.DataFrame(columns=["Name", "Description", "ResponseTemplate", "Priority"])
    
    stream = io.BytesIO()
    df.to_excel(stream, index=False, engine="openpyxl")
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=intent_template.xlsx"}
    )

@app.post("/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db)
):
    passenger_id = From
    message_text = Body

    # ======== Logic ile ile ya /chat =========
    response_text = "Samahani, sijaelewa swali lako."
    intent_id = None

    try:
        detected_intent, fulfillment_text = classify_with_dialogflow(message_text)
        if fulfillment_text:
            response_text = fulfillment_text
            db_intent = db.query(Intent).filter(Intent.Name == detected_intent).first()
            if db_intent:
                intent_id = db_intent.IntentID
        else:
            raise ValueError("Hakuna fulfillmentText kutoka Dialogflow")
    except Exception as e:
        print("Dialogflow error:", e)
        trainer = IntentTrainer(db)
        local_result = trainer.predict(message_text)
        if local_result:
            response_text = local_result["response"]
            intent_id = local_result["intent_id"]

    # ======== Save conversation & messages ========
    conversation = db.query(Conversation).filter_by(PassengerID=passenger_id).first()
    if not conversation:
        conversation = Conversation(PassengerID=passenger_id, ChannelID=1, StartTime=datetime.now())
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    msg_in = Message(PassengerID=passenger_id, ConversationID=conversation.ConversationID,
                     IntentID=intent_id, Text=message_text, Direction="inbound",
                     Type="text", Timestamp=datetime.now())
    msg_out = Message(PassengerID=passenger_id, ConversationID=conversation.ConversationID,
                      IntentID=intent_id, Text=response_text, Direction="outbound",
                      Type="text", Timestamp=datetime.now())
    db.add_all([msg_in, msg_out])
    db.commit()

    # ======== Return TwiML XML ========
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""
    return Response(content=twiml_response, media_type="application/xml")

   
