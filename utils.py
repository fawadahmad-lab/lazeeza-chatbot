import os
import logging
from urllib.parse import quote
import markdown
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_nomic import NomicEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

logger = logging.getLogger("LazizaBot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SUPPORT_PHONE = "+92 333 0960555"
DEFAULT_MESSAGE = "Hi, I need help with my order from Laziza Pulao & Crispo."

database = None
chain = None
retriever = None

user_sessions = {}

def get_whatsapp_url() -> str:
    clean_phone = ''.join(c for c in SUPPORT_PHONE if c.isdigit())
    phone_number = '92' + clean_phone.lstrip('0') if not clean_phone.startswith('92') else clean_phone
    return f"https://wa.me/{phone_number}?text={quote(DEFAULT_MESSAGE)}"

def format_response(response_text: str) -> str:
    return markdown.markdown(response_text)

def initialize_rag_system():
    global database, chain, retriever
    try:
        logger.info("Initializing RAG System...")

        groq_key = os.getenv("GROQ_API_KEY")
        nomic_key = os.getenv("NOMIC_API_KEY")

        if not groq_key or not nomic_key:
            raise EnvironmentError("API keys missing in environment variables.")

        embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5")
        faiss_index_path = "faiss_index"

        if not os.path.exists(faiss_index_path):
            raise FileNotFoundError(f"FAISS index not found at '{faiss_index_path}'. Generate it before deployment.")

        database = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)

        llm = ChatGroq(model="llama-3.3-70b-versatile")
        parser = StrOutputParser()

        prompt_file = "prompt.txt"
        if not os.path.exists(prompt_file):
            raise FileNotFoundError(f"Prompt template '{prompt_file}' not found.")
        with open(prompt_file, "r", encoding="utf-8") as file:
            prompt_text = file.read()

        prompt = PromptTemplate.from_template(prompt_text)

        retriever = database.as_retriever(search_kwargs={"k": 5})
        chain = prompt | llm | parser

        logger.info("RAG System Initialized Successfully.")

    except Exception as e:
        logger.error(f"RAG initialization failed: {str(e)}")
        raise

def get_chain_components():
    if database is None or chain is None or retriever is None:
        raise RuntimeError("RAG system not initialized. Call 'initialize_rag_system()' first.")
    return database, chain, retriever, user_sessions

 