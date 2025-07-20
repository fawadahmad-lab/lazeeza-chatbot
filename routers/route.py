from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import logging
import markdown
from utils import initialize_rag_system, chat_with_rag, get_whatsapp_url

router = APIRouter()
logger = logging.getLogger(__name__)

user_sessions = {}

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    formatted_response: str
    status: str
    redirect: bool = False
    whatsapp_url: str = ""
    awaiting_confirmation: bool = False

def format_response(response_text: str) -> str:
    return markdown.markdown(response_text)

@router.on_event("startup")
async def startup_event():
    try:
        initialize_rag_system()
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")

@router.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    from main import templates
    return templates.TemplateResponse("chat.html", {"request": request})

@router.post("/api/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    user_id = request.user_id or "default"
    user_sessions.setdefault(user_id, {'awaiting_confirmation': False})

    if user_sessions[user_id]['awaiting_confirmation']:
        reply = request.message.lower().strip()
        if reply in ['yes', 'y', 'yeah', 'ok']:
            user_sessions[user_id]['awaiting_confirmation'] = False
            return ChatResponse(
                response="I'm connecting you to our restaurant support team on WhatsApp...",
                formatted_response="I'm connecting you to our restaurant support team on WhatsApp...",
                status="success",
                redirect=True,
                whatsapp_url=get_whatsapp_url(),
                awaiting_confirmation=False
            )
        elif reply in ['no', 'n', 'later']:
            user_sessions[user_id]['awaiting_confirmation'] = False
            return ChatResponse(
                response="No problem! How else can I assist you?",
                formatted_response="No problem! How else can I assist you?",
                status="success",
                redirect=False,
                whatsapp_url="",
                awaiting_confirmation=False
            )
        else:
            return ChatResponse(
                response="I didn't understand. Should I connect you with our human support? (yes/no)",
                formatted_response="I didn't understand. Should I connect you with our human support? (yes/no)",
                status="success",
                redirect=False,
                awaiting_confirmation=True
            )

    try:
        response = chat_with_rag(request.message)
        if response['fallback']:
            user_sessions[user_id]['awaiting_confirmation'] = True
        return ChatResponse(
            response=response['text'],
            formatted_response=format_response(response['text']),
            status="success",
            redirect=response['redirect'],
            whatsapp_url=response.get('whatsapp_url', ""),
            awaiting_confirmation=user_sessions[user_id]['awaiting_confirmation']
        )
    except Exception as e:
        logger.error(f"Error during chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing your request")

@router.get("/api/whatsapp-url")
async def get_whatsapp_url_endpoint():
    return {"whatsapp_url": get_whatsapp_url()}
