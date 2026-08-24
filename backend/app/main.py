from fastapi import FastAPI

from backend.app.api.conversations import router as conversations_router

from backend.app.api.chat import router as chat_router



app = FastAPI(
    title="OSB Chatbot API",
    description="OSB RAG Chatbot Backend API",
    version="1.0.0",
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