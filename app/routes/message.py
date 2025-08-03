import json
import os
from pathlib import Path

@router.get("/conversations/{conversation_id}/faq")
def generate_faq(conversation_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(Message)
        .filter_by(ConversationID=conversation_id)
        .order_by(Message.Timestamp.asc())
        .all()
    )

    faq_list = []
    last_question = None

    for msg in messages:
        if msg.Direction == "inbound":  # User Question
            last_question = msg.Text
        elif msg.Direction == "outbound" and last_question:
            faq_list.append({
                "question": last_question,
                "answer": msg.Text
            })
            last_question = None  # reset after pairing

    # Absolute path to this Python file's directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(BASE_DIR, "faq.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(faq_list, f, indent=4, ensure_ascii=False)

    return {"message": f"{len(faq_list)} FAQs saved to {output_path}", "faq": faq_list}
