from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.utils import get_embedding
from app.services.faiss_manager import search_in_faiss, search_in_faiss_by_filename
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline

router = APIRouter(prefix="/hybrid-qa", tags=["Hybrid QA"])

model_name = "savasy/bert-base-turkish-squad"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)


# ✅ Yeni model
class QuestionRequest(BaseModel):
    question: str
    filename: Optional[str] = None  # Bu eklendi
    top_k: int = 3

# 📌 POST endpoint
@router.post("/")
@router.post("/")
async def hybrid_qa(request: QuestionRequest):
    question = request.question
    top_k = request.top_k

    # 1. Embed oluştur
    query_embedding = get_embedding(question)

    # 2. FAISS ile top_k belge al
    if request.filename:
        results = search_in_faiss_by_filename(query_embedding, request.filename, top_k=top_k)
    else:
        results = search_in_faiss(query_embedding, top_k=top_k)

    if not results:
        return {"message": "Hiçbir eşleşen doküman bulunamadı."}

    # 3. En iyi cevabı seç
    best_result = {"score": 0, "answer": "", "filename": "", "context": ""}

    for result in results:
        context = result["content"]
        filename = result["filename"]

        try:
            qa_result = qa_pipeline(question=question, context=context)
            if qa_result["score"] > best_result["score"]:
                best_result = {
                    "score": qa_result["score"],
                    "answer": qa_result["answer"].strip(),
                    "filename": filename,
                    "context": context
                }
        except Exception as e:
            continue  # hata olan context varsa atla


    return {
        "question": question,
        "answer": best_result["answer"],
        "score": best_result["score"],
        "source_file": best_result["filename"],
        "context": best_result["context"]
    }

