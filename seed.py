# backend/app/seed.py
from app.database import SessionLocal
from app.models.intent import Intent

db = SessionLocal()

intents = [
    Intent(Name="Booking Inquiry", Description="Nataka kuweka tiketi", ResponseTemplate="Unaweza kuweka tiketi mtandaoni au stesheni ya SGR."),
    Intent(Name="Schedule Info", Description="Ratiba ya treni", ResponseTemplate="Treni zinaondoka kila siku saa 2 asubuhi na saa 9 alasiri."),
    Intent(Name="Cancellation Request", Description="Nataka kufuta tiketi", ResponseTemplate="Unaweza kufuta tiketi kwa kutumia akaunti yako ya mtandaoni."),
]

for intent in intents:
    db.add(intent)

db.commit()
db.close()
