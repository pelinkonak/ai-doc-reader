import os
import json
import faiss
import numpy as np

INDEX_PATH = "vector_store/index.faiss"
METADATA_PATH = "vector_store/metadata.json"
EMBED_DIM = 384 # Model embedding boyutu

def load_index_and_metadata():
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(EMBED_DIM)
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        metadata = []
    return index, metadata

def save_index_and_metadata(index, metadata):
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def add_to_faiss(embedding: list, filename: str, content: str):
    index, metadata = load_index_and_metadata()
    embedding_np = np.array([embedding]).astype("float32")
    index.add(embedding_np)
    metadata.append({
        "filename": filename,
        "content": content
    })
    save_index_and_metadata(index, metadata)
    
    print(f"✅ FAISS'e eklendi: {filename} | Vektör boyutu: {len(embedding)}")


def search_in_faiss(query_embedding: list, top_k: int = 1, filename: str = None):
    index, metadata = load_index_and_metadata()
    if index.ntotal == 0:
        return []

    query_np = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query_np, index.ntotal)  # tüm sonuçları al

    results = []
    for i, idx in enumerate(indices[0]):
        if idx >= len(metadata):
            continue

        doc = metadata[idx]

        # Eğer kullanıcı belirli bir dosya istemişse ve bu o dosya değilse atla
        if filename and doc.get("filename") != filename:
            continue

        results.append({
            "score": float(1 / (1 + distances[0][i])),  # L2 mesafesini skora çevir
            "filename": doc.get("filename", "unknown"),
            "content": doc.get("content", "")
        })

        # top_k kadar sonuç toplayınca kır
        if len(results) >= top_k:
            break

    return results


def remove_from_faiss(filename: str):
    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
        return

    index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    indices_to_keep = []
    new_metadata = []

    for i, meta in enumerate(metadata):
        if meta["filename"] != filename:
            indices_to_keep.append(i)
            new_metadata.append(meta)

    if len(indices_to_keep) == len(metadata):
        return  # silinecek bir şey yok

    vectors_to_keep = [index.reconstruct(i) for i in indices_to_keep]
    new_index = faiss.IndexFlatL2(EMBED_DIM)
    new_index.add(np.array(vectors_to_keep).astype("float32"))

    save_index_and_metadata(new_index, new_metadata)

# Örnek global değişkenler
dimension = 384

def rebuild_faiss_index():
    if not os.path.exists(METADATA_PATH):
        return

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    if len(metadata) == 0:
        index = faiss.IndexFlatL2(EMBED_DIM)
    else:
        # Reconstruct ile FAISS içinden embedding'leri al
        index = faiss.read_index(INDEX_PATH)
        embeddings = [index.reconstruct(i) for i in range(len(metadata))]

        index = faiss.IndexFlatL2(EMBED_DIM)
        index.add(np.array(embeddings).astype("float32"))

    faiss.write_index(index, INDEX_PATH)

def search_in_faiss_by_category(query_embedding, top_k=3, category=None):
    index, metadata = load_index_and_metadata()
    if index is None or not metadata:
        return []

    query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)  # ✅ BURAYI EKLE

    D, I = index.search(query_embedding, len(metadata))
    results = []

    for score, idx in zip(D[0], I[0]):
        if idx == -1:
            continue

        doc_meta = metadata[idx]
        if category and doc_meta.get("category") != category:
            continue  # 🔍 Kategori filtresi

        results.append({
            "filename": doc_meta["filename"],
            "content": doc_meta["content"],
            "category": doc_meta.get("category", "Diğer"),
            "score": float(score)
        })

        if len(results) >= top_k:
            break

    return results

def search_in_faiss_by_filename(query_embedding, filename, top_k=3):
    index, metadata = load_index_and_metadata()

    if not metadata:
        return []

    # Embed'e göre en benzerleri bul
    D, I = index.search(query_embedding.reshape(1, -1), len(metadata))  # tüm dokümanlar

    results = []
    for i, idx in enumerate(I[0]):
        if idx < len(metadata):
            item = metadata[idx]
            if item["filename"] == filename:  # sadece eşleşen dosya adına göre filtrele
                results.append({
                    "filename": item["filename"],
                    "content": item["content"],
                    "category": item.get("category", ""),
                    "score": float(D[0][i])
                })
        if len(results) >= top_k:
            break

    return results
