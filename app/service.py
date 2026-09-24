"""
RAG Service — الخدمة الرئيسية
تربط بين: رفع PDF → تحويل Markdown → تقطيع ذكي → تضمين → فهرسة → استرجاع → إجابة
"""
import os
import re
from typing import Dict, Any, List
from app.config import settings
from app.reader import convert_pdf_bytes_to_markdown
from app.chunker import smart_chunk
from app.embedder import Embedder
from app.vector_store import LocalVectorStore
from app.llm import OpenRouterLLM
from app.models import (
    HealthResponse,
    SimpleAskRequest,
    SimpleAnswerResponse,
    UploadResponse,
    SearchResultItem,
)


class RAGService:
    """
    منسق خدمة RAG الرئيسية (Service Layer).
    يربط بين رفع PDF، تحويل Markdown، التقطيع الذكي، التضمين، الفهرسة، والإجابة.
    """
    def __init__(self):
        self.embedder = Embedder()
        self.store = LocalVectorStore(
            collection_name="documents_store",
            storage_dir=settings.vector_db_dir,
        )
        self.llm = OpenRouterLLM()
        self.documents_count = 0
        self.total_chunks = 0

    def process_uploaded_pdf(self, pdf_bytes: bytes, filename: str) -> UploadResponse:
        """
        معالجة ملف PDF مرفوع:
        1. تحويل إلى Markdown عبر LlamaParse API
        2. تقطيع ذكي (MarkdownHeaderSplit + Context Injection)
        3. تضمين وفهرسة في المخزن المتجهي
        """
        # الخطوة 1: تحويل PDF → Markdown
        markdown_text = convert_pdf_bytes_to_markdown(pdf_bytes, filename)
        
        # حفظ نسخة Markdown محلياً (اختياري للمرجعية)
        os.makedirs(settings.upload_dir, exist_ok=True)
        md_path = os.path.join(settings.upload_dir, f"{os.path.splitext(filename)[0]}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        
        # الخطوة 2: التقطيع الذكي
        chunks = smart_chunk(markdown_text, max_chunk_size=500, overlap=80)
        
        if not chunks:
            return UploadResponse(
                message="تم تحويل الملف لكن لم يتم استخراج أي قطع نصية.",
                filename=filename,
                chunks_count=0,
                markdown_preview=markdown_text[:500],
            )
        
        # الخطوة 3: التضمين والفهرسة
        all_texts = [c.text for c in chunks]
        self.embedder.fit_vocabulary(all_texts)
        vectors = self.embedder.embed_batch(all_texts)
        self.store.add_documents(chunks, vectors)
        
        self.documents_count += 1
        self.total_chunks = len(self.store.documents)
        
        return UploadResponse(
            message=f"تم رفع وفهرسة '{filename}' بنجاح.",
            filename=filename,
            chunks_count=len(chunks),
            markdown_preview=markdown_text[:500],
        )

    def simple_ask(self, req: SimpleAskRequest) -> SimpleAnswerResponse:
        """ارسل سؤال واحصل على إجابة نصية واضحة ومباشرة مع مصادرها."""
        raw_q = req.question.strip()
        
        # تنظيف الحروف المتكررة مثل الوووو أو هلاااا
        clean_q = re.sub(r'(.)\1+', r'\1\1', raw_q.lower()).strip()
        clean_q_single = re.sub(r'(.)\1+', r'\1', raw_q.lower()).strip()
        
        # كشف رسائل التحية والترحيب (فقط إذا كانت تحية صرفة بدون سؤال حقيقي)
        greetings = [
            "مرحبا", "مرحباً", "اهلا", "أهلا", "أهلاً", "سلام", "السلام عليكم",
            "صباح الخير", "مساء الخير", "هلا", "هاي", "الو", "الوو", "ألو", "ألوو",
            "هلو", "هللو", "يا هلا", "تحياتي", "hi", "hello", "hey", "halo", "allo"
        ]
        
        # كلمات تدل على وجود سؤال حقيقي بعد التحية
        question_indicators = [
            "عن", "شو", "ما", "ماذا", "كيف", "لماذا", "ليش", "متى", "وين", "أين",
            "من", "هل", "ايش", "إيش", "وش", "كم", "ممكن", "اريد", "أريد", "ابي",
            "عم", "بدي", "اشرح", "وضح", "فسر", "what", "how", "why", "when", "where",
            "?", "؟"
        ]
        
        is_pure_greeting = any(
            clean_q == g or clean_q_single == g
            for g in greetings
        )
        
        # إذا بدأت بتحية لكن تحتوي سؤال حقيقي → لا تعاملها كتحية
        if not is_pure_greeting:
            starts_with_greeting = any(
                clean_q.startswith(g + " ") or clean_q_single.startswith(g + " ")
                for g in greetings
            )
            if starts_with_greeting:
                rest_of_message = clean_q
                for g in sorted(greetings, key=len, reverse=True):
                    if rest_of_message.startswith(g + " "):
                        rest_of_message = rest_of_message[len(g):].strip()
                        break
                has_question = any(ind in rest_of_message for ind in question_indicators)
                if has_question or len(rest_of_message.split()) >= 3:
                    is_pure_greeting = False
                else:
                    is_pure_greeting = True
        
        if is_pure_greeting:
            return SimpleAnswerResponse(
                question=req.question,
                answer="أهلاً وسهلاً بك! كيف يمكنني مساعدتك في الإجابة عن أي استفسار من واقع المستندات المرفوعة؟",
                sources=[],
            )
        
        # التحقق من وجود مستندات مفهرسة
        if self.total_chunks == 0 and len(self.store.documents) == 0:
            return SimpleAnswerResponse(
                question=req.question,
                answer="لا توجد مستندات مفهرسة بعد. يرجى رفع ملف PDF أولاً عبر /api/upload.",
                sources=[],
            )

        query_vec = self.embedder.embed(req.question)
        retrieved_items = self.store.similarity_search(query_vec, k=3)

        # إذا كانت أعلى نتيجة تشابه ضعيفة جداً
        max_score = max([item.score for item in retrieved_items], default=0.0)
        if max_score < 0.08 and not self.llm.is_configured():
            return SimpleAnswerResponse(
                question=req.question,
                answer="عذراً، هذا السؤال غير متوفر في المستندات المتاحة. يرجى طرح سؤال متعلق بمحتوى المستندات المرفوعة.",
                sources=[],
            )

        answer = self.llm.generate_answer(req.question, retrieved_items)

        sources = []
        if "غير متوفرة" not in answer and "لم يتم العثور" not in answer:
            for item in retrieved_items:
                trail = item.chunk.metadata.get("header_trail", "")
                if trail and trail != "عام" and trail not in sources:
                    sources.append(trail)

        return SimpleAnswerResponse(
            question=req.question,
            answer=answer,
            sources=sources,
        )

    def clear_index(self) -> Dict[str, Any]:
        """مسح جميع البيانات المفهرسة."""
        self.store.documents = []
        self.store.vectors = []
        if self.store.chroma_collection is not None:
            try:
                existing = self.store.chroma_collection.get()
                if existing and existing.get("ids"):
                    self.store.chroma_collection.delete(ids=existing["ids"])
            except Exception:
                pass
        self.documents_count = 0
        self.total_chunks = 0
        return {"status": "تم مسح جميع البيانات المفهرسة بنجاح."}

    def get_health(self) -> HealthResponse:
        model_name = (
            self.embedder.model_name
            if self.embedder.using_api
            else f"{self.embedder.model_name} (Active: Built-in Local)"
        )
        return HealthResponse(
            status="healthy",
            documents_indexed=self.documents_count,
            total_chunks=len(self.store.documents),
            openrouter_configured=self.llm.is_configured(),
            llamaparse_configured=bool(settings.llamaparse_api_key and len(settings.llamaparse_api_key) > 10),
            embedding_model=model_name,
            embedding_dimensions=self.embedder.last_dimension,
        )
