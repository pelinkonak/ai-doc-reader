from app.services.utils import get_embedding, guess_category
from app.services.faiss_manager import search_in_faiss_by_category
from transformers import pipeline

# Soru-cevaplama modeli
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

def get_best_answer(question: str, top_k: int = 3, threshold: float = 0.2):
    # 1. Embedding oluştur
    query_embedding = get_embedding(question)

    # 2. Kategori tahmini
    predicted_category = guess_category(question)
    print(f"[INFO] Soru için tahmin edilen kategori: {predicted_category}")

    # 3. FAISS'ten sadece bu kategoriye ait belgeleri getir
    top_docs = search_in_faiss_by_category(query_embedding, top_k=top_k, category=predicted_category)

    if not top_docs:
        return {
            "answer": "İlgili kategoride belge bulunamadı.",
            "score": 0.0,
            "source": ""
        }

    # 4. En iyi cevabı bul
    best_result = {"answer": "", "score": 0.0, "source": ""}

    for doc in top_docs:
        print(f"[INFO] QA çalışıyor: {doc['filename']} (Kategori: {doc['category']})")
        context = doc["content"]
        try:
            result = qa_pipeline(question=question, context=context)
            if result["score"] > best_result["score"]:
                best_result.update({
                    "answer": result["answer"],
                    "score": result["score"],
                    "source": doc["filename"]
                })
        except Exception as e:
            print(f"[ERROR] {doc['filename']} için QA başarısız: {e}")
            continue

    # 5. Eşik kontrolü
    if best_result["score"] < threshold:
        return {
            "answer": "Bu soruya yeterli güvenle cevap verilemiyor.",
            "score": best_result["score"],
            "source": best_result["source"]
        }

    return best_result
