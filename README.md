---

# 🥘 Laziza Pulao & Crispo - AI Chat Assistant

> AI-powered customer support assistant for **Laziza Pulao & Crispo**, a restaurant in Rawalpindi, Pakistan.
> Built with **FastAPI**, **LangChain RAG**, and **Nomic Embeddings**.

---

##  Project Overview

This project is an AI chatbot system designed to assist restaurant customers by answering menu-related questions, prices, deals, and common queries.
It combines **Retrieval-Augmented Generation (RAG)** with **FastAPI** for a responsive, production-ready backend.

---

## 🛠️ Features

* ✅ **RAG-based Question Answering** using LangChain + FAISS
* ✅ **Nomic Embeddings** for document search
* ✅ Integrated with **ChatGroq's LLaMA 3.3 Model**
* ✅ WhatsApp Human Support Integration
* ✅ Clean HTML/Javascript Frontend Chat Widget
* ✅ Markdown to HTML response formatting
* ✅ PDF Knowledge Base Loader
* ✅ FastAPI Production-ready Server

---

## 🗂️ Tech Stack

| Technology    | Purpose               |
| ------------- | --------------------- |
| **FastAPI**   | Web Framework         |
| **LangChain** | RAG and LLM Pipelines |
| **Nomic AI**  | Embedding Model       |
| **ChatGroq**  | LLM API               |
| **FAISS**     | Vector Store          |
| **Markdown**  | Response Formatting   |
| **Jinja2**    | HTML Templating       |

---

## 📄 How it Works

1️⃣ **PDF Document Loader**
→ Loads the restaurant menu and FAQs from a cleaned PDF

2️⃣ **Chunk Splitter & FAISS Vector Store**
→ Splits content into manageable chunks and stores embeddings

3️⃣ **User Query Handler (Chat Endpoint)**
→ Accepts user message, retrieves context, passes through LLM

4️⃣ **Fallback Handling**
→ If no confident response, offers WhatsApp contact

5️⃣ **Markdown Formatting**
→ LLM response formatted to clean HTML for frontend display

---

## 💡 Deployment Ready Features

* ✔️ Environment variable-based secrets
* ✔️ FAISS index reusable after build
* ✔️ Custom startup RAG initialization
* ✔️ Routes separated (API + Static)
* ✔️ Ready for Docker / Nginx Deployment
* ✔️ Cleaned response formatting

---

## 📝 Usage Example

```http
POST /api/chat

{
  "message": "What are your combo deals?"
}
```

Returns

```json
{
  "response": "Here's our combo deals ...",
  "formatted_response": "<p>Here's our combo deals ...</p>",
  "status": "success",
  "redirect": false,
  "whatsapp_url": "",
  "awaiting_confirmation": false
}
```

---

## ⚡ Live Demo / Deployment

> This repository is only for code demonstration.
> The production instance is running on private servers.
> Deployment-ready with Uvicorn/Gunicorn & Nginx.

---

## 📂 Project Structure

```
/Laziza_bot
├── main.py                  # FastAPI app entry point
├── utils.py                 # Helper functions (RAG, WhatsApp)
├── routers/                 # FastAPI routers
├── templates/               # Jinja2 HTML files
├── static/                  # Static assets (JS)
├── styles/                  # CSS files
├── faiss_index/             # Generated FAISS index (required)
├── prompt.txt               # LLM formatted prompt template
├── requirements.txt         
├── .env                     # Environment variables (GROQ_API_KEY, etc.)
```

---

## 🔐 Important Note

> The production code and FAISS index are **kept private**.
> This repository is for showcasing project structure, architecture, and concept only.

---

## 🧑‍💻 Author

**Fawad Qureshi**
AI/ML Engineer
[LinkedIn](https://www.linkedin.com/in/fawadqureshi-mlengineer/) | [Portfolio](https://my-portfolio-onebeta-93.vercel.app/)

---

## 📝 License

MIT License — Free to use for educational & demonstration purposes.

---
