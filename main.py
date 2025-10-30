from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import (ai_config_router, auth_router, chat_router,
                     dashboard_router)
from app.api import mpp_service_router as service
from app.api import user_chat_router

app = FastAPI(
    title="Chatbot RAG Sewakadharma",
    description="Chatbot layanan publik Kota Denpasar dengan RAG & Gemini",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "Haloo! Semoga harimu menyenangkan",
        "tips": "Gunakan endpoint /docs untuk eksplorasi API ini!"
    } 

# Auth endpoints (public)
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])

# Admin endpoints (protected - need JWT token)
app.include_router(dashboard_router.router, prefix="/admin/dashboard", tags=["Admin - Dashboard"])
app.include_router(service.router, prefix="/admin/services", tags=["Admin - Services"])
app.include_router(ai_config_router.router, prefix="/admin/ai-config", tags=["Admin - AI Config"])
app.include_router(chat_router.router, prefix="/admin/test-chat", tags=["Admin - Test Chat"])

# User endpoints (public)
app.include_router(user_chat_router.router, prefix="/chat", tags=["User Chat"])