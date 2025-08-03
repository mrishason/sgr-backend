import json
import sqlite3
import os

# Load conversation flows from JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "conversation_flows.json"), "r") as f:
    CONVERSATION_FLOWS = json.load(f)

def detect_intent(user_message: str):
    # Example simple intent detection using DB
    conn = sqlite3.connect("sgr.db")
    c = conn.cursor()
    c.execute("SELECT intent_name FROM intents")  # simple approach
    intents = [row[0] for row in c.fetchall()]
    conn.close()
    
    # Simple match (You can replace with NLP)
    for intent in intents:
        if intent in user_message.lower():
            return intent
    # fallback
    if "train" in user_message.lower() or "treni" in user_message.lower():
        return "train_schedule"
    return None

# Temporary conversation state (in memory)
USER_STATES = {}

def get_response(user_id: str, message: str):
    # Check if user has active flow
    if user_id in USER_STATES:
        state = USER_STATES[user_id]
        intent = state["intent"]
        step = state["step"] + 1
        flow = CONVERSATION_FLOWS.get(intent, [])
        
        if step < len(flow):
            USER_STATES[user_id]["step"] = step
            return flow[step]["message"]
        else:
            del USER_STATES[user_id]
            return "Asante, mazungumzo yamekamilika."

    # New message → detect intent
    intent = detect_intent(message)
    if intent and intent in CONVERSATION_FLOWS:
        USER_STATES[user_id] = {"intent": intent, "step": 0}
        return CONVERSATION_FLOWS[intent][0]["message"]

    return "Samahani, sijaelewa. Tafadhali uliza tena."
