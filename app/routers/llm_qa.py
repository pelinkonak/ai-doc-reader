from fastapi import APIRouter
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

router = APIRouter(prefix="/llm-qa", tags=["LLM QA"])

# Model setup
model_name = "google/flan-t5-base"
token = "hf_xxx"  # Hugging Face tokenını buraya yaz

tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, token=token)

llm_pipe = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=200
)

class LLMQARequest(BaseModel):
    question: str

@router.post("/")
async def ask_with_llm(request: LLMQARequest):
    prompt = request.question.strip()

    if not prompt:
        return {"error": "Soru boş olamaz."}

    try:
        response = llm_pipe(prompt)
        return {
            "question": request.question,
            "answer": response[0]["generated_text"]
        }
    except Exception as e:
        return {"error": "LLM işleminde hata oluştu.", "details": str(e)}
