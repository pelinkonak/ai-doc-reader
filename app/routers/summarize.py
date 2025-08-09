from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.summarizer import summarize_text

router = APIRouter(prefix="/summarize", tags=["Summarization"])

class TextInput(BaseModel):
    text: str

@router.post("/")
async def summarize(input: TextInput):
    if not input.text.strip():
        raise HTTPException(status_code=400, detail="Metin boş olamaz.")

    summary = summarize_text(input.text)

    if not summary:
        return {"summary": "Özetleme başarısız veya içerik yetersiz."}

    return {"summary": summary}
