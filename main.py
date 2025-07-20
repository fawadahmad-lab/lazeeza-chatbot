from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import chat, whatsapp
from utils import initialize_rag_system

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/styles",StaticFiles(directory='styles'),name='style')
templates = Jinja2Templates(directory="templates")

app.include_router(chat.router)
app.include_router(whatsapp.router)

@app.on_event("startup")
async def startup_event():
    initialize_rag_system()

@app.get("/")
async def home():
    return templates.TemplateResponse("chat.html", {"request": {}})

