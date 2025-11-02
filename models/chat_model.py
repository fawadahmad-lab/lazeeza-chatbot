from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    formatted_response: str
    status: str
    redirect: bool = False
    whatsapp_url: str = ""
    awaiting_confirmation: bool = False

