from transformers import pipeline
import joblib
import os

# Question Answering pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Dummy context - replace or move to DB later
context = """
SGR trains run between Nairobi and Mombasa.
Trains depart at 8:00 AM and 3:00 PM daily.
Tickets can be booked online or at SGR stations.
Cancellations allowed up to 24 hours before departure.
First class: 3000 Tsh, Economy: 1000 Tsh.
"""


# Intent classification - load model if trained
def classify_intent(text: str) -> str:
    if os.path.exists("intent_model.pkl") and os.path.exists("vectorizer.pkl"):
        model = joblib.load("intent_model.pkl")
        vectorizer = joblib.load("vectorizer.pkl")
        X = vectorizer.transform([text])
        return model.predict(X)[0]
    return "General Inquiry"

def answer_question(question: str) -> str:
    try:
        result = qa_pipeline(question=question, context=context)
        return result["answer"] if result["score"] > 0.1 else "Samahani, sijaelewa swali lako."
    except:
        return "Samahani, sijaweza kupata jibu kwa sasa."
