from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os  

# Proje kökündeki .env dosyasını yükle
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

import openai

api_key = os.getenv("OPENAI_API_KEY")
print("🔑 API KEY yüklendi mi?", api_key[:10] if api_key else None)

openai.api_key = api_key


# Router'ları içeri aktar
from app.routers import (
    upload,
    search,
    summarize,
    qa,
    multi_qa,
    hybrid_qa,
    hybrid_chain_qa,
    faiss_admin,
    faiss_ops,
    llm_qa,
    openai_qa
    
)
from app.routers import feedback  # doğru klasör: routes

# Uygulama başlat
app = FastAPI(title="AI Doc Reader")

# Frontend local portuna CORS izni ver (5173–5179 arası güvenli)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:3000",
        "http://127.0.0.1:3000",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tüm router'ları FastAPI app'e ekle
app.include_router(upload.router)
app.include_router(search.router)
app.include_router(summarize.router)
app.include_router(qa.router)
app.include_router(multi_qa.router)
app.include_router(hybrid_qa.router)
app.include_router(hybrid_chain_qa.router)
app.include_router(faiss_admin.router)
app.include_router(faiss_ops.router)
app.include_router(llm_qa.router)
app.include_router(feedback.router)
app.include_router(openai_qa.router)

# Ana sayfa endpoint
@app.get("/", response_class=HTMLResponse)
def root():
    return "<h1>API çalışıyor 🚀</h1>"
