from app.database import SessionLocal
from app.models.channel import Channel
from datetime import datetime

db = SessionLocal()
channels = [
    {
        "Name": "web",
        "ConfigDetails": "",
        "Status": "active",
        "LastUpdated": datetime.utcnow()
    },
    {
        "Name": "whatsapp",
        "ConfigDetails": '{"twilioNumber": "+14155238886"}',
        "Status": "active",
        "LastUpdated": datetime.utcnow()
    }
]

for c in channels:
    existing = db.query(Channel).filter_by(Name=c["Name"]).first()
    if not existing:
        db.add(Channel(**c))
db.commit()
db.close()
