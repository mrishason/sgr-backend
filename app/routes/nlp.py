# app/routes/nlp.py
import json
import requests
from fastapi import APIRouter
from pydantic import BaseModel
import google.auth
import google.auth.transport.requests

router = APIRouter(prefix="/nlp", tags=["NLP"])

class Message(BaseModel):
    text: str

def get_access_token():
    """Get Google OAuth2 token from service account"""
    credentials, project_id = google.auth.default()
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token, project_id

def classify_with_dialogflow(text: str):
    token, project_id = get_access_token()

    session_id = "123456"  # you can use random or user-specific session id
    url = f"https://dialogflow.googleapis.com/v2/projects/{project_id}/agent/sessions/{session_id}:detectIntent"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "queryInput": {
            "text": {
                "text": text,
                "languageCode": "en"
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Dialogflow Error: {response.text}")

    result = response.json()
    intent_name = result["queryResult"]["intent"]["displayName"]
    fulfillment_text = result["queryResult"].get("fulfillmentText", "")

    return intent_name, fulfillment_text

@router.post("/classify")
def classify(msg: Message):
    intent, response = classify_with_dialogflow(msg.text)
    return {"intent": intent, "response": response}
