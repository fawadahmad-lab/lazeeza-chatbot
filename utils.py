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
from globals.var import SUPPORT_PHONE, DEFAULT_MESSAGE

load_dotenv()

logger = logging.getLogger("LazizaBot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

support_phn = SUPPORT_PHONE
default_msg = DEFAULT_MESSAGE

database = None
chain = None
retriever = None
user_sessions = {}

def get_whatsapp_url() -> str:
    """Generate WhatsApp URL with default message"""
    clean_phone = ''.join(c for c in SUPPORT_PHONE if c.isdigit())
    phone_number = '92' + clean_phone.lstrip('0') if not clean_phone.startswith('92') else clean_phone
    return f"https://wa.me/{phone_number}?text={quote(DEFAULT_MESSAGE)}"

def format_response(response_text: str) -> str:
    """Convert plain text to Markdown-formatted HTML"""
    return markdown.markdown(response_text)

def initialize_rag_system():
    """Initialize FAISS database, embeddings, LLM, and chain with prompt"""
    global database, chain, retriever
    try:
        logger.info("Initializing RAG System...")

        groq_key = os.getenv("GROQ_API_KEY")
        nomic_key = os.getenv("NOMIC_API_KEY")

        if not groq_key or not nomic_key:
            raise EnvironmentError("API keys missing in environment variables.")

        # Initialize embeddings and database
        embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5")
        faiss_index_path = "faiss_index"

        if not os.path.exists(faiss_index_path):
            raise FileNotFoundError(f"FAISS index not found at '{faiss_index_path}'. Generate it before deployment.")

        database = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)

        # Initialize LLM and output parser
        llm = ChatGroq(model="llama-3.3-70b-versatile")
        parser = StrOutputParser()

        prompt_text = f"""
You are a professional, friendly, and intelligent customer service chatbot for Laziza Pulao & Crispo,
a popular family restaurant in Rawalpindi, Pakistan.

⚡ CORE RULES
- Always answer relevant questions directly.
- Start with a direct answer. Yes/No questions start with "Yes" or "No."
- Never say "I don't know" or "I'm not sure."
- ONLY provide the WhatsApp contact button when the query is COMPLETELY outside the context provided or unrelated to restaurant operations.
- If the context contains relevant information, answer based on it even if incomplete.

🍴 RESTAURANT CONTEXT SCOPE
- Menu items, prices, ingredients
- Operating hours, location, contact info
- Delivery, takeaway, dining options
- Recipes, food preparation methods
- Restaurant policies, offers, promotions
- Any food and beverage related queries

🚫 OUT-OF-CONTEXT EXAMPLES (show WhatsApp button):
- Questions about other businesses
- Technical support for websites/apps
- Personal advice or non-food topics
- Politics, sports, entertainment
- Questions completely unrelated to restaurant operations

🗣️ RESPONSE BEHAVIOR
- Relevant question within context → answer directly and helpfully
- Query partially related but missing details → answer what you can and suggest WhatsApp for specifics
- Query completely outside context → provide WhatsApp button ONLY
- Keep answers concise and focused

✅ FORMAT INSTRUCTIONS
- For in-context queries: Provide direct answer only, NO WhatsApp button
- For out-of-context queries: Provide ONLY the WhatsApp HTML below, no additional text

WHATSAPP BUTTON HTML (ONLY for out-of-context queries):
<div>
  <p>I'm not familiar with '{{input}}' — for personalized assistance, click the WhatsApp icon below to chat with our human representative.</p>
  <a href="{get_whatsapp_url()}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; text-decoration:none; background:#25D366; color:white; padding:6px 12px; border-radius:6px; font-weight:bold;">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="white">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347"/>
    </svg>
    Chat on WhatsApp
  </a>
</div>

DECISION FLOW:
1. Check if query relates to restaurants, food, menu, delivery, location, hours, or any context provided
2. IF related → Answer directly without WhatsApp button
3. IF completely unrelated → Provide ONLY the WhatsApp HTML above

FINAL TEMPLATE
Context Information:
{{context}}

Customer Query:
{{input}}

Your Response:
"""


        prompt = PromptTemplate.from_template(prompt_text)

        # Create retriever
        retriever = database.as_retriever(search_kwargs={"k": 5})
        chain = prompt | llm | parser

        logger.info("RAG System Initialized Successfully.")

    except Exception as e:
        logger.error(f"RAG initialization failed: {str(e)}")
        raise

def get_chain_components():
    """Return initialized database, chain, retriever, and user sessions"""
    if database is None or chain is None or retriever is None:
        raise RuntimeError("RAG system not initialized. Call 'initialize_rag_system()' first.")
    return database, chain, retriever, user_sessions
