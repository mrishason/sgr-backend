from pydantic import BaseModel

class IntentCreate(BaseModel):
    Name: str
    Description: str
    ResponseTemplate: str
    Priority: int