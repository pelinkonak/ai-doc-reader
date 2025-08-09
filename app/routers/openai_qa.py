# routers/openai_qa.py
from fastapi import APIRouter
from pydantic import BaseModel
import openai
import os 
from dotenv import load_dotenv
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/openai-qa", tags=["OpenAI QA"])

openai.api_key = "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"

class QARequest(BaseModel):
    question: str
    filenames: list[str] = []

@router.post("/")
async def openai_qa(request: QARequest):
    # Belgeleri oku ve context hazırla
    docs = []
    for filename in request.filenames:
        try:
            with open(f"uploads/{filename}", "r", encoding="utf-8") as f:
                docs.append(f.read())
        except Exception as e:
            continue  # Dosya yoksa atla

    # Context'i sınırla (token limiti için), istersen ilk 2-3 dosya ile başla
    context = "\n---\n".join(docs[:3])

    prompt = f"""
Aşağıdaki belgelerin içeriğine göre soruyu cevapla. 
Eğer cevabın belgelerde yazıyorsa sadece belgelerdeki bilgilere dayanarak cevap ver.
Eğer belgelerde bu bilgi yoksa önce "Belgelerde bu bilgi yok." yaz ve ardından kendi genel bilgi ve yorumunu ekle.
Belgeler dışındaki dünya bilgini sadece ikinci durumda kullanabilirsin.

{context}
---
Soru: {request.question}
Cevap:
"""

    response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=512,
    temperature=0.2,
)
    answer = response.choices[0].message.content.strip()

    # Sonra kategori için yeni bir prompt oluştur
    category_prompt = f"""
Cevap: {answer}
Bu cevabın teması nedir? SADECE bir kelimeyle, ana kategori olarak dön: (ör: Sağlık, Eğitim, Finans, Tarım, Teknoloji, Hukuk, Genel, vb.)
"""
    cat_response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": category_prompt}],
    max_tokens=10,
    temperature=0.0,
)
    predicted_category = cat_response.choices[0].message.content.strip()


    return {
        "answer": answer,
        "context": context[:400] + "..." if len(context) > 400 else context,
        "source_file": ", ".join(request.filenames) if request.filenames else "",
        "score": 1.0,  # OpenAI yanıtları için dummy skor
        "predicted_category": predicted_category,
    }
