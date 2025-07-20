from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils import get_chain_components, get_whatsapp_url, format_response

router = APIRouter(prefix="/api", tags=["Chat"])

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

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        database, chain, retriever, user_sessions = get_chain_components()
        user_message = request.message.strip()
        user_id = request.user_id

        if user_id not in user_sessions:
            user_sessions[user_id] = {'awaiting_confirmation': False}

        if user_sessions[user_id]['awaiting_confirmation']:
            if user_message.lower() in ['yes', 'y', 'yeah', 'sure', 'ok', 'okay']:
                user_sessions[user_id]['awaiting_confirmation'] = False
                return ChatResponse(
                    response="I'm connecting you to our restaurant support team on WhatsApp...",
                    formatted_response="I'm connecting you to our restaurant support team on WhatsApp...",
                    status="success",
                    redirect=True,
                    whatsapp_url=get_whatsapp_url()
                )
            elif user_message.lower() in ['no', 'n', 'not now', 'later']:
                user_sessions[user_id]['awaiting_confirmation'] = False
                return ChatResponse(
                    response="No problem! How else can I assist you with our menu today?",
                    formatted_response="No problem! How else can I assist you with our menu today.",
                    status="success"
                )
            else:
                return ChatResponse(
                    response="I didn't understand. Would you like me to connect you with our human support team on WhatsApp? (yes/no)",
                    formatted_response="I didn't understand. Would you like me to connect you with our human support team on WhatsApp? (yes/no)",
                    status="success",
                    awaiting_confirmation=True
                )

        if database is None or chain is None:
            return ChatResponse(
                response="Our system is currently unavailable. Let me connect you with human support.",
                formatted_response="Our system is currently unavailable. Let me connect you with human support.",
                status="success",
                redirect=True,
                whatsapp_url=get_whatsapp_url()
            )

        context = "\n".join([doc.page_content for doc in retriever.invoke(user_message)])
        raw_response = chain.invoke({"context": context, "input": user_message})

        fallback_phrases = ["I'm not sure", "I don't know", "Sorry", "unable to help", "I couldn't find"]
        if any(phrase.lower() in raw_response.lower() for phrase in fallback_phrases):
            user_sessions[user_id]['awaiting_confirmation'] = True
            fallback_message = """I couldn't find information about that in our menu.  
Would you like to connect with our staff on WhatsApp?  
Reply with 'yes' to connect or 'no' to continue."""
            return ChatResponse(
                response=fallback_message,
                formatted_response=format_response(fallback_message),
                status="success",
                awaiting_confirmation=True
            )

        return ChatResponse(
            response=raw_response,
            formatted_response=format_response(raw_response),
            status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
