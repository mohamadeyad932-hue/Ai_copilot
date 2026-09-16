from typing import List, Dict
from app.models import DocumentChunkModel


def bad_chunking(raw_text: str, chunk_size: int = 40, overlap: int = 0) -> List[DocumentChunkModel]:
    """
    التقطيع السيء (Bad Chunking):
    1. حجم صغير جداً (40 حرفاً).
    2. صفر تداخل (Overlap = 0).
    3. قطع عشوائي لمنتصف الكلمات وضياع السياق.
    """
    chunks = []
    text_clean = " ".join(raw_text.split())
    
    start = 0
    chunk_index = 0
    while start < len(text_clean):
        end = start + chunk_size
        chunk_text = text_clean[start:end]
        
        doc_id = f"BAD-CHUNK-{chunk_index:03d}"
        metadata = {
            "strategy": "Bad Chunking (Rigid small char split)",
            "chunk_index": chunk_index,
            "char_count": len(chunk_text),
            "chunk_size_config": chunk_size,
            "overlap_config": overlap
        }
        chunks.append(DocumentChunkModel(id=doc_id, text=chunk_text, metadata=metadata))
        
        start += (chunk_size - overlap)
        chunk_index += 1
        
    return chunks


def good_chunking(articles: List[Dict[str, str]], target_chunk_size: int = 250, overlap: int = 50) -> List[DocumentChunkModel]:
    """
    التقطيع الجيد (Good Chunking):
    1. واعٍ ببنية المستند (Article-Aware).
    2. مراعاة حدود الكلمات والفقرات.
    3. حجم متوازن مع تداخل (Overlap = 50 حرفاً).
    4. إرفاق Metadata غنية بالمعلومات.
    """
    chunks = []
    
    for art in articles:
        content = art["content"]
        art_id = art["article_id"]
        art_title = art["title"]
        
        if len(content) <= target_chunk_size * 1.4:
            doc_id = f"GOOD-{art_id}-C00"
            metadata = {
                "strategy": "Good Chunking (Semantic Article-Aware)",
                "article_id": art_id,
                "article_title": art_title,
                "chunk_index": 0,
                "char_count": len(content),
                "is_full_article": True
            }
            chunks.append(DocumentChunkModel(id=doc_id, text=content, metadata=metadata))
            continue
            
        words = content.split()
        current_chunk_words = []
        current_len = 0
        art_chunk_idx = 0
        
        for word in words:
            current_chunk_words.append(word)
            current_len += len(word) + 1
            
            if current_len >= target_chunk_size:
                chunk_text = " ".join(current_chunk_words)
                doc_id = f"GOOD-{art_id}-C{art_chunk_idx:02d}"
                metadata = {
                    "strategy": "Good Chunking (Sliding Window with Overlap)",
                    "article_id": art_id,
                    "article_title": art_title,
                    "chunk_index": art_chunk_idx,
                    "char_count": len(chunk_text),
                    "is_full_article": False
                }
                chunks.append(DocumentChunkModel(id=doc_id, text=chunk_text, metadata=metadata))
                
                overlap_words = []
                overlap_len = 0
                for w in reversed(current_chunk_words):
                    if overlap_len + len(w) + 1 <= overlap:
                        overlap_words.insert(0, w)
                        overlap_len += len(w) + 1
                    else:
                        break
                        
                current_chunk_words = overlap_words
                current_len = sum(len(w) + 1 for w in current_chunk_words)
                art_chunk_idx += 1
                
        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            doc_id = f"GOOD-{art_id}-C{art_chunk_idx:02d}"
            metadata = {
                "strategy": "Good Chunking (Sliding Window with Overlap)",
                "article_id": art_id,
                "article_title": art_title,
                "chunk_index": art_chunk_idx,
                "char_count": len(chunk_text),
                "is_full_article": False
            }
            chunks.append(DocumentChunkModel(id=doc_id, text=chunk_text, metadata=metadata))
            
    return chunks
