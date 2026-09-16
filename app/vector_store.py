import os
import math
from typing import List
from app.models import DocumentChunkModel, SearchResultItem

try:
    import chromadb
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False


class LocalVectorStore:
    """
    مخزن المتجهات مع دعم ChromaDB الكامل:
    - ينشئ PersistentClient في مجلد vector_db لتخزين وفهرسة المتجهات والـ Metadata والـ Document IDs.
    - ينفذ بحث التشابه الدلالي بواسطة Cosine Similarity من ChromaDB.
    - يحتوي على محرك مدمج احتياطي في حال عدم إمكانية تحميل مكتبة ChromaDB.
    """
    def __init__(self, collection_name: str, storage_dir: str = "vector_db"):
        self.collection_name = collection_name
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        self.documents: List[DocumentChunkModel] = []
        self.vectors: List[List[float]] = []
        self.chroma_collection = None
        
        if HAS_CHROMADB:
            try:
                self.client = chromadb.PersistentClient(path=self.storage_dir)
                self.chroma_collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"تعذر فتح ChromaDB PersistentClient ({e}) - اعتماد المحرك المحلي الاحتياطي.")

    def add_documents(self, docs: List[DocumentChunkModel], vectors: List[List[float]]):
        self.documents = docs
        self.vectors = vectors
        
        if self.chroma_collection is not None and docs:
            ids = [doc.id for doc in docs]
            documents = [doc.text for doc in docs]
            
            metadatas = [
                {k: (str(v) if isinstance(v, (dict, list)) else v) for k, v in doc.metadata.items()}
                for doc in docs
            ]
            
            try:
                existing = self.chroma_collection.get()
                if existing and existing.get("ids"):
                    self.chroma_collection.delete(ids=existing["ids"])
            except Exception:
                pass

            self.chroma_collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=vectors
            )

    def similarity_search(self, query_vector: List[float], k: int = 3) -> List[SearchResultItem]:
        if self.chroma_collection is not None:
            try:
                count = self.chroma_collection.count()
                if count > 0:
                    n_results = min(k, count)
                    results = self.chroma_collection.query(
                        query_embeddings=[query_vector],
                        n_results=n_results
                    )
                    
                    search_items = []
                    if results and results.get("ids") and results["ids"][0]:
                        ids = results["ids"][0]
                        docs = results["documents"][0]
                        metas = results["metadatas"][0]
                        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)
                        
                        for doc_id, text, meta, dist in zip(ids, docs, metas, distances):
                            score = max(0.0, min(1.0, 1.0 - dist))
                            chunk = DocumentChunkModel(id=doc_id, text=text, metadata=meta)
                            search_items.append(SearchResultItem(chunk=chunk, score=round(score, 4)))
                            
                        return search_items
            except Exception as e:
                print(f"خطأ أثناء بحث ChromaDB ({e}) - التبديل للحساب المحلي.")

        scored = []
        for doc, vec in zip(self.documents, self.vectors):
            score = self._cosine_similarity(query_vector, vec)
            scored.append(SearchResultItem(chunk=doc, score=round(score, 4)))
            
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:k]

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
