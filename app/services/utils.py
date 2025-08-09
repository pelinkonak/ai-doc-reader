from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException
from sentence_transformers import SentenceTransformer

def extract_text_from_html(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

# Modeli sadece bir kez yükle
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str):
    embedding = model.encode(text)
    print("Embedding boyutu:", len(embedding))
    return embedding.tolist()

import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip() 

# ✅ Otomatik Kategori Tahmini
def guess_category(text: str) -> str:
    text_lower = text.lower()

    if any(keyword in text_lower for keyword in [
        "ai", "artificial intelligence", "machine learning", "deep learning", "neural network",
        "yapay zeka", "makine öğrenmesi", "derin öğrenme", "sinir ağı"
    ]):
        return "Yapay Zeka"

    elif any(keyword in text_lower for keyword in [
        "health", "medicine", "patient", "doctor", "medical",
        "sağlık", "hasta", "doktor", "tedavi", "tıp"
    ]):
        return "Sağlık"

    elif any(keyword in text_lower for keyword in [
        "finance", "stock", "investment", "economy", "cryptocurrency",
        "finans", "borsa", "yatırım", "ekonomi", "kripto"
    ]):
        return "Finans"

    elif any(keyword in text_lower for keyword in [
        "software", "programming", "python", "javascript", "code", "developer",
        "yazılım", "programlama", "kod", "geliştirici"
    ]):
        return "Yazılım"

    elif any(keyword in text_lower for keyword in [
        "law", "legal", "court", "contract", "attorney",
        "hukuk", "mahkeme", "sözleşme", "avukat", "yasal"
    ]):
        return "Hukuk"

    else:
        return "Diğer"
