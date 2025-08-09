from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import pipeline

# --- 1. PDF'i yükle
pdf_path = "ornek.pdf"
docs = PyPDFLoader(pdf_path).load()

# --- 2. Chunk'lara ayır
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
chunks = splitter.split_documents(docs)

# --- 3. Embedding ve vektör veritabanı
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma.from_documents(chunks, embeddings)

# --- 4. En iyi chunk'ı bul (semantic search)
soru = "Bu belgenin ana konusu nedir?"
docs_and_scores = vectordb.similarity_search_with_score(soru, k=2)
best_context = docs_and_scores[0][0].page_content

# --- 5. QA pipeline'ı kullan
qa_pipeline = pipeline(
    "question-answering",
    model="savasy/bert-base-turkish-squad",
    tokenizer="savasy/bert-base-turkish-squad"
)
result = qa_pipeline(question=soru, context=best_context)
print("Cevap:", result["answer"])

