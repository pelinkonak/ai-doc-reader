# 🤖 AI Doc Reader

Yapay zekâ destekli belge analiz ve sorgulama sistemi.  
Kullanıcılar HTML veya PDF belgeleri yükleyerek bu belgelerin:
- içeriğini analiz edebilir,  
- dilini algılayabilir,  
- özetini çıkarabilir,  
- benzer içerikleri arayabilir  
- ve doğal dilde sorular sorabilir.  

---

## 🎯 Projenin Amacı

Yüklenen dokümanların semantik olarak analiz edilip işlenmesi ve anlamlı sorgulara cevap verebilen bir altyapı sunmak.

### ✔️ Şu an desteklenen işlemler:
- 📤 HTML/PDF yükleme
- 🌐 Dil tespiti (`langdetect`)
- 🔎 Metin gövdesi çıkarımı (`BeautifulSoup`, `PyMuPDF`)
- 🧠 Embedding üretimi (`Sentence Transformers`)
- 💾 FAISS ile benzerlik tabanlı arama
- 📝 Otomatik özetleme (`facebook/bart-large-cnn`)
- ❓ Soru-cevap sistemi (`deepset/roberta-base-squad2`, Türkçe için `savasy/bert-base-turkish-squad`)

---

## 🗂️ Klasör Yapısı

ai-doc-reader/
├── app/
│ ├── main.py
│ ├── routers/
│ │ ├── upload.py
│ │ ├── search.py
│ │ ├── summarize.py
│ │ └── qa.py
│ └── services/
│ ├── utils.py
│ ├── faiss_manager.py
│ └── summarizer.py
├── data/ # Yüklenen belgeler
├── vector_store/ # FAISS index + metadata
├── requirements.txt
└── README.md


---

## ⚙️ Kurulum

Gereksinimleri yüklemek için:
```bash
pip install -r requirements.txt
Model dosyalarının ilk çalıştırmada indirileceğini unutma (özellikle özetleme ve QA için).

🚀 API Sunucusu

uvicorn app.main:app --reload --port 8001
API arayüzüne git:
🔗 http://127.0.0.1:8001/docs

📤 HTML Yükleme

curl -X 'POST' http://127.0.0.1:8001/upload/html \
  -F 'file=@data/yapayzeka.html;type=text/html'

📤 PDF Yükleme

curl -X 'POST' http://127.0.0.1:8001/upload/pdf \
  -F 'file=@data/deneme.pdf;type=application/pdf'

🔍 Benzer İçerik Arama

curl -X 'POST' http://127.0.0.1:8001/search/ \
  -H 'Content-Type: application/json' \
  -d '{ "query": "doğal dil işleme" }'

📝 Metin Özetleme

curl -X 'POST' http://127.0.0.1:8001/summarize/ \
  -H 'Content-Type: application/json' \
  -d '{ "text": "Yapay zekâ günümüzde birçok sektörde etkili..." }'

❓ Soru-Cevap

curl -X 'POST' http://127.0.0.1:8001/qa/ \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Yapay zekâ neden önemlidir?",
    "context": "Yapay zekâ, iş süreçlerini otomatikleştirerek verimliliği artırmakta ve insan gücünü desteklemektedir."
  }'


Kullanılan Teknolojiler

FastAPI – REST API geliştirme
BeautifulSoup / PyMuPDF – HTML ve PDF metin çıkarımı
langdetect – Dil algılama
Sentence Transformers – Vektör (embedding) oluşturma
FAISS – Semantik arama motoru
Transformers (🤗) – Özetleme ve Soru-Cevap modelleri


Sonraki Aşamalar

 🔁 Belgelerden otomatik özet çıkarma (yükleme anında)
 🔍 Tüm belgelerden “en uygun” cevabı verme
 🧾 Özet + QA + metin içeriği birlikte görsel arayüzde gösterme
 🧠 HuggingFace API ile model deploy (yerel yük yerine dış servis)
 🌐 Basit bir frontend (HTML/JS)


👨‍💻 Geliştirici Notu

Bu proje, gerçek dünyada belge yönetimi, arama ve içerik analizi gerektiren sistemler için temel bir altyapı sunmayı amaçlamaktadır.
Eğitim, Ar-Ge, hukuk, finans ve içerik arşivleme sistemlerinde uygulanabilir bir yapıdır.



