from app.services.faiss_manager import load_index_and_metadata, search_in_faiss
from app.services.utils import get_embedding
from transformers import pipeline
from app.services.faiss_manager import search_in_faiss

# Daha uyumlu bir model tercih edildi, örneğin bert-base-multilingual-cased
qa_pipeline = pipeline(
    "question-answering",
    model="bert-base-multilingual-cased",
    tokenizer="bert-base-multilingual-cased",
    tokenizer_kwargs={"use_fast": False}  # veya istenirse kaldırılabilir
)


def hybrid_question_answering(question: str, top_k: int = 3):
    query_embedding = get_embedding(question)
    results = search_in_faiss(query_embedding, top_k=top_k)

    if not results:
        return None

    best_result = {
        "score": 0,
        "answer": "",
        "filename": "",
        "context": ""
    }

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
            print(f"QA Pipeline Error for {filename}: {e}")
            continue

    return best_result if best_result["score"] > 0.1 else None
