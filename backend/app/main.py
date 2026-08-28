from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.conversations import router as conversations_router

from backend.app.api.chat import router as chat_router



app = FastAPI(
    title="OSB Chatbot API",
    description="OSB RAG Chatbot Backend API",
    version="1.0.0",
)

# Arayüz ayrı bir statik sunucudan (veya yerel dosyadan) açılabildiği için
# tarayıcının API çağrılarını engellememesi gerekir. API sözleşmesini veya
# RAG akışını değiştirmez.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "osb-chatbot-api",
    }
    
app.include_router(
    conversations_router
)

app.include_router(chat_router)
