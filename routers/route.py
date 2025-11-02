from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models.chat_model import ChatRequest, ChatResponse
import logging
from utils import initialize_rag_system, get_whatsapp_url, format_response
from routers.chat import chat_with_bot

router = APIRouter()
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

user_sessions = {}

@router.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    try:
        logger.info("Initializing RAG system...")
        initialize_rag_system()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        raise

@router.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    """Serve the main chat interface"""
    try:
        templates = Jinja2Templates(directory="templates")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error serving home page: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



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


@router.post("/api/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """Handle chat messages from users using the bot"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # Call the main chat bot function
        response: ChatResponse = await chat_with_bot(request)

        # Ensure WhatsApp redirect URL is always set if redirect=True
        if response.redirect:
            response.whatsapp_url = get_whatsapp_url()
            # Always embed WhatsApp button in formatted_response
            response.formatted_response = build_whatsapp_button_message(response.response)
        else:
            # Ensure formatted_response exists for normal messages
            if not response.formatted_response:
                response.formatted_response = format_response(response.response)

        return response

    except Exception as e:
        logger.error(f"Error during chat processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing your request")



@router.get("/api/whatsapp-url")
async def get_whatsapp_url_endpoint():
    """Get WhatsApp URL for direct chat"""
    return {"whatsapp_url": get_whatsapp_url()}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Laziza Pulao Chatbot"}
