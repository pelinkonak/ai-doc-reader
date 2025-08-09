from fastapi import APIRouter
from app.services.faiss_manager import remove_from_faiss

router = APIRouter()

@router.delete("/faiss/delete/{filename}")
def delete_document_from_faiss(filename: str):
    # Belgeyi FAISS'ten ve metadata'dan sil
    remove_from_faiss(filename)

    return {"status": f"{filename} silindi ve FAISS index yeniden oluşturuldu."}
