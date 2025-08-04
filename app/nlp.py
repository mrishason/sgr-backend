# app/nlp.py
# NLP Trainer simplified (no HuggingFace pipeline, no heavy PyTorch)

class IntentTrainer:
    def __init__(self, db):
        self.db = db

    def predict(self, message: str):
        """
        Simple fallback NLP (can be replaced with real ML model later)
        """
        text = message.lower()

        # Simple keyword-based classification
        if "booking" in text or "tiketi" in text:
            return {"intent_id": None, "response": "Je utahitaji kuweka booking ya ticket au una hitaji maelezo ya ziada?\n1. Book Tiketi\n2. Maelezo ya ziada\n3. Anza upya"}

        if "msaada" in text or "help" in text:
            return {"intent_id": None, "response": "Unaweza kuwasiliana na huduma kwa wateja kupitia namba 0800-11-00."}

        # Default fallback
        return {"intent_id": None, "response": "Samahani, sijaelewa swali lako."}
