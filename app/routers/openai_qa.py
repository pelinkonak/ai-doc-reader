# routers/openai_qa.py
from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF ile PDF okuma

# .env yükle
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter(prefix="/openai-qa", tags=["OpenAI QA"])

# 📂 Dosyaların kaydedildiği klasör (upload.py ile aynı olmalı!)
UPLOAD_DIR = "data"

class QARequest(BaseModel):
    question: str
    filenames: list[str] = []

@router.post("/")
async def openai_qa(request: QARequest):
    # Belgeleri oku ve context hazırla
    docs = []
    for filename in request.filenames:
        try:
            filepath = os.path.join(UPLOAD_DIR, filename)
            if filename.endswith(".pdf"):
                text = ""
                doc = fitz.open(filepath)
                for page in doc:
                    text += page.get_text("text")
                docs.append(text)
            else:
                with open(filepath, "r", encoding="utf-8") as f:
                    docs.append(f.read())
        except Exception as e:
            print("❌ Dosya okunamadı:", filename, e)
            continue  # Dosya yoksa veya okunamazsa atla

    # Context'i sınırla (token limiti için), ilk 2-3 dosya ile başla
    context = "\n---\n".join(docs[:3])
    print("📄 Context içerik:", context[:1000])  # ilk 1000 karakteri yaz

    if not context.strip():
        return {"error": "PDF içeriği boş geldi. Eğer belge taranmış (image-based) ise OCR (ör. pytesseract) gerekebilir."}
    
    prompt = f"""
Aşağıda belgelerden alınan parçalar var. Kullanıcının sorusunu sadece bu parçalardaki bilgiye dayanarak yanıtla. 
Belgelerde doğrudan aynı ifade geçmese bile, benzer anlamlı kısımları kullanarak çıkarım yapabilirsin. 
Eğer belgelerde ilgili bilgi yoksa önce "Belgelerde bu bilgi direkt cümle şeklinde bulunmuyor." yaz ve sonra kendi genel bilginle cevap verebilirsin. 
Ama belgelerde cevap varsa mutlaka onlara dayanarak cevap ver.

{context}
---
Soru: {request.question}
Cevap:
"""

    # OpenAI cevabı
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # istersen "gpt-3.5-turbo" da kullanabilirsin
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.2,
    )
    answer = response.choices[0].message.content.strip()

    # Kategori için yeni prompt
    category_prompt = f"""
Cevap: {answer}
Bu cevabın teması nedir? SADECE bir kelimeyle, ana kategori olarak dön: 
(ör: Sağlık, Eğitim, Finans, Tarım, Teknoloji, Hukuk, Genel, vb.)
"""

    cat_response = client.chat.completions.create(
        model="gpt-4o-mini",
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
