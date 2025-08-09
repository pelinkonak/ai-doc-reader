from fastapi import APIRouter
import os
import json
import faiss

from app.services.faiss_manager import INDEX_PATH, METADATA_PATH, save_index_and_metadata

router = APIRouter(prefix="/faiss", tags=["FAISS Admin"])


@router.post("/reset")
def reset_faiss():
    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)
    if os.path.exists(METADATA_PATH):
        os.remove(METADATA_PATH)

    # Yeni boş index ve metadata oluştur
    index = faiss.IndexFlatL2(384)  # Embedding boyutun neyse o
    metadata = []
    save_index_and_metadata(index, metadata)

    return {"status": "FAISS index ve metadata sıfırlandı ✅"}


@router.get("/list")
def list_filenames_only():
    """
    Sadece dosya adlarını döner: ["doc1.pdf", "doc2.html", ...]
    """
    if not os.path.exists(METADATA_PATH):
        return {"documents": []}

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    filenames = [doc.get("filename", "unknown") for doc in metadata]
    return {"documents": filenames}


@router.get("/list/detailed")
def list_documents_detailed():
    """
    Her belge için detaylı bilgi döner: dosya adı, karakter sayısı, içerik önizlemesi
    """
    if not os.path.exists(METADATA_PATH):
        return {"documents": []}

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    result = []
    for i, doc in enumerate(metadata):
        filename = doc.get("filename", "unknown")
        content = doc.get("content", "")
        filetype = doc.get("filetype", "unknown")
        uploaded_at = doc.get("uploaded_at", "N/A")

        result.append({
            "index": i,
            "filename": filename,
            "filetype": filetype,
            "char_count": len(content),
            "preview": content[:100] + ("..." if len(content) > 100 else ""),
            "uploaded_at": uploaded_at
        })

    return {"documents": result}
