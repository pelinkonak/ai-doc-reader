from fastapi import APIRouter
from pydantic import BaseModel
from app.services.utils import get_embedding
from app.services.faiss_manager import search_in_faiss

router = APIRouter(prefix="/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str

@router.post("/")
async def search_documents(request: SearchRequest):
    query_embedding = get_embedding(request.query)
    results = search_in_faiss(query_embedding, top_k=1)

    if not results:
        return {"message": "Henüz kayıtlı veri bulunamadı."}
    
    return {
        "query": request.query,
        "result": results[0]
    }
