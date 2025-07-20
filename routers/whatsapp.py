from fastapi import APIRouter
from utils import get_whatsapp_url

router = APIRouter(prefix="/api", tags=["WhatsApp"])

@router.get("/whatsapp-url")
async def get_whatsapp_url_endpoint():
    return {
        "whatsapp_url": get_whatsapp_url(),
        "support_phone": "+92 333 0960555"
    }
