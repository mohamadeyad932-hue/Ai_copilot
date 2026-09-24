"""
Chunker — تقطيع ذكي للنص Markdown بتقنيتين:
1. التقطيع حسب العناوين (MarkdownHeaderTextSplitter)
2. حقن السياق (Context Injection) لكل قطعة
"""
import re
from typing import List, Dict, Tuple, Optional
from app.models import DocumentChunkModel


# ─── التقنية الأولى: التقطيع حسب العناوين ───

# تعريف مستويات العناوين في Markdown
HEADER_LEVELS: List[Tuple[str, str]] = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]


def _detect_header(line: str) -> Optional[Tuple[str, str]]:
    """
    اكتشاف ما إذا كان السطر عنوان Markdown.
    يعيد (مستوى العنوان, نص العنوان) أو None.
    """
    stripped = line.strip()
    for prefix, level in HEADER_LEVELS:
        # يجب أن يتبع الرمز # مسافة مباشرة
        if stripped.startswith(prefix + " ") and not stripped.startswith(prefix + "#"):
            header_text = stripped[len(prefix):].strip()
            if header_text:
                return (level, header_text)
    return None


def markdown_header_split(markdown_text: str) -> List[Dict]:
    """
    التقطيع حسب العناوين (MarkdownHeaderTextSplitter):
    - يمسح النص سطراً بسطر.
    - عند مصادفة عنوان (#, ##, ###) يفتح قسماً جديداً.
    - يُخزن شجرة العناوين (header trail) في البيانات الوصفية لكل قطعة.
    
    Returns:
        قائمة من القواميس: [{"content": str, "metadata": {"h1": ..., "h2": ..., "h3": ...}}]
    """
    lines = markdown_text.split("\n")
    
    # حالة تتبع العناوين الحالية
    current_headers: Dict[str, str] = {}
    
    sections: List[Dict] = []
    current_content_lines: List[str] = []
    
    for line in lines:
        header_info = _detect_header(line)
        
        if header_info:
            level, header_text = header_info
            
            # حفظ القسم السابق إن وُجد محتوى
            content = "\n".join(current_content_lines).strip()
            if content:
                sections.append({
                    "content": content,
                    "metadata": dict(current_headers),
                })
            current_content_lines = []
            
            # تحديث شجرة العناوين:
            # عند ظهور h1 جديد → مسح h2 و h3
            # عند ظهور h2 جديد → مسح h3
            if level == "h1":
                current_headers = {"h1": header_text}
            elif level == "h2":
                current_headers = {
                    k: v for k, v in current_headers.items() if k == "h1"
                }
                current_headers["h2"] = header_text
            elif level == "h3":
                current_headers = {
                    k: v for k, v in current_headers.items() if k in ("h1", "h2")
                }
                current_headers["h3"] = header_text
        else:
            current_content_lines.append(line)
    
    # حفظ القسم الأخير
    content = "\n".join(current_content_lines).strip()
    if content:
        sections.append({
            "content": content,
            "metadata": dict(current_headers),
        })
    
    return sections


# ─── التقنية الثانية: حقن السياق ───

def _build_context_prefix(metadata: Dict[str, str]) -> str:
    """
    بناء سلسلة السياق من شجرة العناوين.
    مثال: [الفصل الأول > ساعات العمل > التعويضات]
    """
    parts = []
    for level in ("h1", "h2", "h3"):
        if level in metadata and metadata[level]:
            parts.append(metadata[level])
    
    if not parts:
        return ""
    
    return "[" + " > ".join(parts) + "] "


def inject_context(sections: List[Dict]) -> List[Dict]:
    """
    حقن السياق (Context Injection):
    يُضاف مسار شجرة العناوين كبادئة لكل قطعة نصية.
    
    قبل: "السعر: 50 دولار"
    بعد: "[المنتجات > الهواتف > آيفون 13] السعر: 50 دولار"
    
    هذا يحول الـ Vector إلى تمثيل دلالي دقيق ولا يفقد معناه.
    """
    enriched = []
    for section in sections:
        prefix = _build_context_prefix(section["metadata"])
        enriched_content = prefix + section["content"]
        enriched.append({
            "content": enriched_content,
            "metadata": section["metadata"],
            "context_prefix": prefix.strip() if prefix else "",
        })
    return enriched


# ─── تجميع النتائج في DocumentChunkModel ───

def _sub_split_large_section(text: str, max_chunk_size: int = 500, overlap: int = 80) -> List[str]:
    """
    تقسيم فرعي للأقسام الكبيرة جداً مع الحفاظ على حدود الجمل.
    """
    if len(text) <= max_chunk_size * 1.3:
        return [text]
    
    # محاولة التقسيم على حدود الجمل
    sentence_endings = re.compile(r'(?<=[.،؟!:\n])\s+')
    sentences = sentence_endings.split(text)
    
    sub_chunks = []
    current = ""
    
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chunk_size and current:
            sub_chunks.append(current.strip())
            # حساب التداخل: أخذ آخر جزء من القطعة السابقة
            words = current.split()
            overlap_words = []
            overlap_len = 0
            for w in reversed(words):
                if overlap_len + len(w) + 1 <= overlap:
                    overlap_words.insert(0, w)
                    overlap_len += len(w) + 1
                else:
                    break
            current = " ".join(overlap_words) + " " + sentence if overlap_words else sentence
        else:
            current = (current + " " + sentence).strip() if current else sentence
    
    if current.strip():
        sub_chunks.append(current.strip())
    
    return sub_chunks if sub_chunks else [text]


def smart_chunk(markdown_text: str, max_chunk_size: int = 500, overlap: int = 80) -> List[DocumentChunkModel]:
    """
    التقطيع الذكي الكامل:
    1. تقطيع حسب العناوين (MarkdownHeaderTextSplitter)
    2. حقن السياق (Context Injection)
    3. تقسيم فرعي للأقسام الكبيرة
    4. إنتاج DocumentChunkModel مع Metadata غنية
    
    Args:
        markdown_text: النص بتنسيق Markdown
        max_chunk_size: الحجم الأقصى لكل قطعة بالأحرف
        overlap: عدد أحرف التداخل بين القطع المتتالية
        
    Returns:
        قائمة من DocumentChunkModel جاهزة للتضمين والفهرسة
    """
    # الخطوة 1: التقطيع حسب العناوين
    sections = markdown_header_split(markdown_text)
    
    # الخطوة 2: حقن السياق
    enriched_sections = inject_context(sections)
    
    # الخطوة 3 و 4: التقسيم الفرعي وبناء النماذج
    chunks: List[DocumentChunkModel] = []
    global_idx = 0
    
    for section in enriched_sections:
        sub_texts = _sub_split_large_section(section["content"], max_chunk_size, overlap)
        
        for sub_idx, sub_text in enumerate(sub_texts):
            doc_id = f"CHUNK-{global_idx:04d}"
            
            # بناء Metadata غنية
            metadata = {
                "strategy": "MarkdownHeaderSplit + ContextInjection",
                "chunk_index": global_idx,
                "sub_chunk_index": sub_idx,
                "total_sub_chunks": len(sub_texts),
                "char_count": len(sub_text),
                "context_prefix": section.get("context_prefix", ""),
            }
            # إضافة معلومات شجرة العناوين
            for level in ("h1", "h2", "h3"):
                if level in section["metadata"]:
                    metadata[level] = section["metadata"][level]
            
            # تجميع عنوان القطعة للعرض
            header_trail = " > ".join(
                section["metadata"].get(l, "") 
                for l in ("h1", "h2", "h3") 
                if section["metadata"].get(l)
            )
            metadata["header_trail"] = header_trail or "عام"
            
            chunks.append(DocumentChunkModel(
                id=doc_id,
                text=sub_text,
                metadata=metadata,
            ))
            
            global_idx += 1
    
    return chunks
