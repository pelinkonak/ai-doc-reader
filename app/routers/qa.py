from fastapi import APIRouter
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline


model_name = "distilbert-base-uncased-distilled-squad"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

router = APIRouter(prefix="/qa", tags=["QuestionAnswering"])

class QARequest(BaseModel):
    question: str
    context: str

@router.post("/")
async def ask_question(request: QARequest):
    if not request.question.strip() or not request.context.strip():
        return {"error": "Soru ve bağlam (context) boş olamaz."}

    result = qa_pipeline(question=request.question, context=request.context)
    return {
        "question": request.question,
        "answer": result["answer"],
        "score": result["score"]
    } 