from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.settings import Settings

# 📂 Adım 1 – Belgeleri oku
documents = SimpleDirectoryReader("data").load_data()

# ⚙️ Adım 2 – Embedding & Index ayarı
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 🧠 Adım 3 – Index oluştur
index = VectorStoreIndex.from_documents(documents)

# ❓ Adım 4 – Soru-cevap
query_engine = index.as_query_engine()
response = query_engine.query("Yapay zekâ sağlık alanında nasıl kullanılır?")
print(response)
