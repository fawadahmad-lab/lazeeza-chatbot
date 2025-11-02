from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils import get_chain_components, get_whatsapp_url, format_response
from models.chat_model import ChatRequest , ChatResponse




router = APIRouter(prefix="/api", tags=["Chat"])
def build_whatsapp_button_message(message_text: str) -> str:
    """
    Returns HTML for a WhatsApp clickable button/icon.
    """
    whatsapp_url = get_whatsapp_url()
    html = f"""
    <p>{message_text}</p>
    <a href="{whatsapp_url}" target="_blank" class="whatsapp-button" style="
        display:inline-flex;
        align-items:center;
        background-color:#25D366;
        color:white;
        padding:8px 12px;
        border-radius:5px;
        text-decoration:none;
        font-weight:bold;
        margin-top:5px;
    ">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="white" style="margin-right:6px;">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347"/>
        </svg>
        Chat on WhatsApp
    </a>
    """
    return html


@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        database, chain, retriever, user_sessions = get_chain_components()
        user_message = request.message.strip()
        user_id = request.user_id or "default"

        # Initialize session if not exists
        if user_id not in user_sessions:
            user_sessions[user_id] = {'awaiting_confirmation': False}

        # Handle ongoing WhatsApp confirmation flow
        if user_sessions[user_id]['awaiting_confirmation']:
            reply = user_message.lower()
            if reply in ['yes', 'y', 'yeah', 'sure', 'ok', 'okay']:
                user_sessions[user_id]['awaiting_confirmation'] = False
                msg = "Connecting you to our restaurant support team on WhatsApp..."
                return ChatResponse(
                    response=msg,
                    formatted_response=build_whatsapp_button_message(msg),
                    status="success",
                    redirect=True,
                    whatsapp_url=get_whatsapp_url()
                )
            elif reply in ['no', 'n', 'not now', 'later']:
                user_sessions[user_id]['awaiting_confirmation'] = False
                msg = "No problem! How else can I assist you with our menu today?"
                return ChatResponse(
                    response=msg,
                    formatted_response=format_response(msg),
                    status="success",
                    redirect=False
                )
            else:
                msg = "I didn't understand. Would you like me to connect you with our human support team on WhatsApp? (yes/no)"
                return ChatResponse(
                    response=msg,
                    formatted_response=build_whatsapp_button_message(msg),
                    status="success",
                    awaiting_confirmation=True,
                    redirect=True,
                    whatsapp_url=get_whatsapp_url()
                )

        # If database or chain is unavailable, fallback to WhatsApp
        if database is None or chain is None:
            msg = "Our system is currently unavailable. Let me connect you with human support."
            return ChatResponse(
                response=msg,
                formatted_response=build_whatsapp_button_message(msg),
                status="success",
                redirect=True,
                whatsapp_url=get_whatsapp_url()
            )

        # Retrieve relevant context and generate bot response
        context = "\n".join([doc.page_content for doc in retriever.invoke(user_message)])
        raw_response = chain.invoke({"context": context, "input": user_message})

        # Define fallback detection phrases
        fallback_phrases = ["I'm not sure", "I don't know", "Sorry", "unable to help", "I couldn't find"]

        # If the bot is unsure, redirect immediately to WhatsApp
        if any(phrase.lower() in raw_response.lower() for phrase in fallback_phrases):
            user_sessions[user_id]['awaiting_confirmation'] = False
            
            fallback_message = (
                f"I'm not familiar with '{user_message}' in our menu — for personalized assistance, "
                f"click the WhatsApp icon below to chat with our human representative."
            )
            return ChatResponse(
                response=fallback_message,
                formatted_response=format_response(fallback_message),
                status="success",
                redirect=True,
                whatsapp_url=get_whatsapp_url()
            )

        # Normal bot response
        return ChatResponse(
            response=raw_response,
            formatted_response=format_response(raw_response),
            status="success",
            redirect=False
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
