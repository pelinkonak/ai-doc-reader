from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline

# --- 1. Belgeyi yükle
pdf_path = "ornek.pdf"  # PDF dosyanın adı
docs = []
docs.extend(PyPDFLoader(pdf_path).load())

# --- 2. Chunk'lara ayır
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
chunks = splitter.split_documents(docs)

# --- 3. Embedding ve vektör veritabanı
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma.from_documents(chunks, embeddings)

# --- 4. Türkçe QA modeli ile pipeline kur
qa_pipeline = pipeline(
    "question-answering",
    model="savasy/bert-base-turkish-squad",
    tokenizer="savasy/bert-base-turkish-squad"
)
llm = HuggingFacePipeline(pipeline=qa_pipeline)

# --- 5. Retrieval QA zinciri
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever()
)

# --- 6. Soru sor
soru = "Bu belgenin ana konusu nedir?"
cevap = qa_chain.invoke({"query": soru})
print("Cevap:", cevap["result"])

