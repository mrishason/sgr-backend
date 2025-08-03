from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from app.models.intent import Intent

class IntentTrainer:
    def __init__(self, db: Session):
        self.db = db
        self.vectorizer = TfidfVectorizer()
        self.intent_map = []  # [(intent_id, text, response_template)]
        self.trained = False

    def train(self):
        intents = self.db.query(Intent).all()
        corpus = []
        self.intent_map = []

        for intent in intents:
            combined_text = f"{intent.Name} {intent.Description}"
            corpus.append(combined_text)
            self.intent_map.append((intent.IntentID, combined_text, intent.ResponseTemplate))

        if corpus:
            self.vectors = self.vectorizer.fit_transform(corpus)
            self.trained = True

    def predict(self, user_input: str):
        if not self.trained:
            self.train()

        input_vector = self.vectorizer.transform([user_input])
        similarities = cosine_similarity(input_vector, self.vectors)
        best_index = similarities.argmax()
        best_score = similarities[0][best_index]

        if best_score < 0.3:
            return None  # Confidence too low

        return {
            "intent_id": self.intent_map[best_index][0],
            "response": self.intent_map[best_index][2],
            "confidence": best_score
        }
    
    
