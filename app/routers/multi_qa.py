from fastapi import APIRouter
from pydantic import BaseModel
from app.services.utils import get_embedding, guess_category
from app.services.faiss_manager import search_in_faiss_by_category
from transformers import pipeline

router = APIRouter(prefix="/multi-qa", tags=["MultiDocumentQA"])

qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

class QuestionInput(BaseModel):
    question: str
    top_k: int = 3  # İsteğe bağlı olarak top_k verilebilir

@router.post("/")
async def multi_document_qa(input: QuestionInput):
    query_embedding = get_embedding(input.question)
    predicted_category = guess_category(input.question)
    print(f"[INFO] Soru için tahmin edilen kategori: {predicted_category}")

    results = search_in_faiss_by_category(query_embedding, top_k=input.top_k, category=predicted_category)

    if not results:
        return {
            "message": "İlgili kategoride eşleşen doküman bulunamadı.",
            "predicted_category": predicted_category
        }

    answers = []
    for result in results:
        try:
            qa_result = qa_pipeline(question=input.question, context=result["content"])
            if qa_result["score"] >= 0.1:
                answers.append({
                    "filename": result["filename"],
                    "score": qa_result["score"],
                    "answer": qa_result["answer"].strip(),
                    "context": result["content"],
                    "category": result.get("category", "Bilinmiyor")
                })
        except Exception as e:
            print(f"[ERROR] {result['filename']} için QA başarısız: {e}")
            continue

    return {
        "predicted_category": predicted_category,
        "answers": answers
    }
