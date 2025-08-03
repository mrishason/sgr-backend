from fastapi import APIRouter, Request
from fastapi.responses import Response

router = APIRouter()

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    message = form_data.get("Body")
    sender = form_data.get("From")

    if not message or not sender:
        return Response(content="Invalid", media_type="text/xml")

    reply = chat_logic(message, passenger_id=1)

    # Return TwiML (XML) response so Twilio sends reply
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply}</Message>
</Response>"""

    return Response(content=twiml_response, media_type="text/xml")

