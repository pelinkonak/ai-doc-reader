from transformers import pipeline

# HuggingFace summarization pipeline
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text: str, max_length=130, min_length=30) -> str:
    text = text.strip()
    
    if not text:
        return "Metin boş."

    # DistilBART genelde 1024 token ile sınırlıdır, kesme yapabiliriz
    if len(text) > 2000:
        text = text[:2000]  # Aşırı uzun metinlerde modeli boğmamak için

    try:
        summary = summarizer(
            text, max_length=max_length, min_length=min_length, do_sample=False
        )
        return summary[0]['summary_text']
    except Exception as e:
        return f"Özetleme başarısız oldu: {str(e)}"
