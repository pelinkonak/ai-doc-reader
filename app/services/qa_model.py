from transformers import pipeline

# Sadece bir kez yüklenir
qa_pipeline = pipeline(
    "question-answering",
    model="deepset/roberta-base-squad2",
    tokenizer="deepset/roberta-base-squad2"
)

def answer_question(question: str, context: str):
    result = qa_pipeline(question=question, context=context)
    return {
        "question": question,
        "answer": result["answer"],
        "score": result["score"]
    }
