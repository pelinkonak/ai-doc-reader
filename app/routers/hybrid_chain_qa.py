from fastapi import APIRouter
from app.services.faiss_manager import remove_from_faiss

router = APIRouter()

@router.delete("/faiss/delete/{filename}")
def delete_document_from_faiss(filename: str):
    # Belgeyi FAISS'ten ve metadata'dan sil
    remove_from_faiss(filename)

    return {"status": f"{filename} silindi ve FAISS index yeniden oluşturuldu."}
 
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.utils import get_embedding
from app.services.faiss_manager import search_in_faiss
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering

model_name = "distilbert-base-uncased-distilled-squad"

# Tokenizer ve model ayrı ayrı yükleniyor ve use_fast=False zorlanıyor
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# Hafif ve hızlı model
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)


router = APIRouter(prefix="/hybrid-chain-qa", tags=["HybridChainQA"])

class QuestionRequest(BaseModel):
    question: str

@router.post("/")
async def hybrid_chain_qa(request: QuestionRequest):
    question = request.question

    # 1. Embedding oluştur
    query_embedding = get_embedding(question)

    # 2. FAISS üzerinden en benzer 3 dokümanı bul
    top_docs = search_in_faiss(query_embedding, top_k=3)

    if not top_docs:
        return {"message": "Hiçbir doküman bulunamadı."}

    # 3. Bu dokümanların içeriklerini birleştir (context chain)
    combined_context = "\n".join([doc["content"] for doc in top_docs if doc["content"]])

    # 4. QA modeline tek seferde gönder
    try:
        response = qa_pipeline(question=question, context=combined_context)
        return {
            "question": question,
            "answer": response["answer"],
            "score": response["score"],
            "sources": [doc["filename"] for doc in top_docs]
        }
    except Exception as e:
        return {"message": "Cevaplama sırasında hata oluştu.", "error": str(e)}