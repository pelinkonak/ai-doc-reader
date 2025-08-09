from fastapi import APIRouter, UploadFile, File
import os
from datetime import datetime
from app.services.utils import guess_category


from app.services.summarizer import summarize_text
from app.services.utils import (
    extract_text_from_html,
    extract_text_from_pdf,
    detect_language,
    get_embedding
)
from app.services.faiss_manager import add_to_faiss, remove_from_faiss

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ HTML Yükleme
@router.post("/html")
async def upload_html(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    try:
        extracted_text = extract_text_from_html(file_location)
        lang = detect_language(extracted_text)
        embedding = get_embedding(extracted_text)
        summary = summarize_text(extracted_text)
        category = guess_category(extracted_text)

        # 🔁 Varsa eski kayıtları kaldır
        remove_from_faiss(file.filename)

        # ✅ FAISS'e kaydet
        add_to_faiss(embedding, file.filename, extracted_text, category)

        return {
            "filename": file.filename,
            "status": "HTML dosyası yüklendi, okundu ve analiz edildi ✅",
            "language": lang,
            "embedding": embedding[:5],
            "summary": summary,
            "content": extracted_text,
            "category": category
        }

    except Exception as e:
        return {
            "status": "HTML yüklendi ama analiz edilemedi ❌",
            "error": str(e)
        }

# ✅ PDF Yükleme
@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    try:
        extracted_text = extract_text_from_pdf(file_location)
        lang = detect_language(extracted_text)
        embedding = get_embedding(extracted_text)
        summary = summarize_text(extracted_text)
        category = guess_category(extracted_text)

        # 🔁 Varsa eski kayıtları kaldır
        remove_from_faiss(file.filename)

        # ✅ FAISS'e kaydet
        add_to_faiss(embedding, file.filename, extracted_text, category)

        return {
            "filename": file.filename,
            "status": "PDF dosyası yüklendi, okundu ve analiz edildi ✅",
            "language": lang,
            "embedding": embedding[:5],
            "summary": summary,
            "content": extracted_text,
            "category": category
        }

    except Exception as e:
        return {
            "status": "PDF yüklendi ama analiz edilemedi ❌",
            "error": str(e)
        }
