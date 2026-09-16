import os
from typing import Dict, Any
from app.config import settings
from app.reader import read_text_file, parse_articles
from app.chunker import bad_chunking, good_chunking
from app.embedder import Embedder
from app.vector_store import LocalVectorStore
from app.llm import OpenRouterLLM
from app.models import (
    SearchQuery,
    SearchResponse,
    ChunkingComparisonResult,
    RAGRequest,
    RAGResponse,
    HealthResponse,
    SimpleAskRequest,
    SimpleAnswerResponse
)


class RAGService:
    """
    منسق خدمة RAG الرئيسية (Service Layer).
    يربط بين قراءة البيانات، التقطيع، التضمين، مخازن المتجهات المحلية، وتوليد الإجابات من OpenRouter LLM.
    """
    def __init__(self):
        self.embedder = Embedder()
        self.good_store = LocalVectorStore(collection_name="good_chunks_store", storage_dir=settings.vector_db_dir)
        self.bad_store = LocalVectorStore(collection_name="bad_chunks_store", storage_dir=settings.vector_db_dir)
        self.llm = OpenRouterLLM()
        self.articles_count = 0

    def initialize_and_index(self, data_file_path: str = None) -> Dict[str, Any]:
        path = data_file_path or settings.data_file_path
        
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            sample_data = """المادة 1: نطاق سريان اللائحة
تسري أحكام هذه اللائحة على جميع الموظفين والمتدربين في الشركة، وتحدد حقوقهم وواجباتهم الوظيفية.

المادة 2: ساعات العمل الرسمية
تكون ساعات العمل الرسمية 8 ساعات يومياً تبدأ من الساعة 8 صباحاً حتى 4 مساءً، بمعدل 40 ساعة أسبوعياً. يحق للإدارة تعديل المواعيد خلال شهر رمضان المبارك.

المادة 3: العمل الإضافي والتعويض
يُحسب العمل الإضافي بموافقة خطية مسبقة من المدير المباشر، ويكون أجر الساعة الإضافية معادلاً لأجر الساعة العادية مضافاً إليه 50% من الراتب الأساسي.

المادة 4: الإجازة السنوية
يستحق الموظف إجازة سنوية مدفوعة الأجر مدتها 30 يوماً عن كل عام من أعوام الخدمة، ولا يجوز النزول عنها أو التنازل عن مقابلها المالي إلا بموافقة مجلس الإدارة.

المادة 5: إنهاء عقد العمل
يجوز لأي من الطرفين إنهاء العقد غير محدد المدة بإشعار خطي مدته لا تقل عن 60 يوماً قبل موعد الإنهاء، وفي حال عدم الالتزام بالإشعار يدفع الطرف المخالف تعويضاً يعادل أجر مهلة الإشعار."""
            with open(path, "w", encoding="utf-8") as f:
                f.write(sample_data)

        raw_text = read_text_file(path)
        articles = parse_articles(raw_text)
        self.articles_count = len(articles)

        bad_chunks = bad_chunking(raw_text, chunk_size=35, overlap=0)
        good_chunks = good_chunking(articles, target_chunk_size=200, overlap=40)

        all_texts = [c.text for c in bad_chunks] + [c.text for c in good_chunks]
        self.embedder.fit_vocabulary(all_texts)

        bad_vectors = self.embedder.embed_batch([c.text for c in bad_chunks])
        good_vectors = self.embedder.embed_batch([c.text for c in good_chunks])

        self.bad_store.add_documents(bad_chunks, bad_vectors)
        self.good_store.add_documents(good_chunks, good_vectors)

        return {
            "status": "success",
            "articles_indexed": len(articles),
            "good_chunks_count": len(good_chunks),
            "bad_chunks_count": len(bad_chunks)
        }

    def search_and_compare(self, query_in: SearchQuery) -> SearchResponse:
        query_vec = self.embedder.embed(query_in.query)

        good_results = self.good_store.similarity_search(query_vec, k=query_in.top_k)
        bad_results = self.bad_store.similarity_search(query_vec, k=query_in.top_k)

        top_good = good_results[0] if good_results else None
        top_bad = bad_results[0] if bad_results else None

        analysis_text = (
            "التقطيع الجيد يسترجع مادة كاملة بسياقها وحكمها الصريح والبيانات الوصفية، "
            "بينما التتقطيع السيء يبتر الأحكام في منتصف الجملة ويعيد قطعاً متفرقة بدون سياق مفيد."
        )

        comparison = ChunkingComparisonResult(
            query=query_in.query,
            bad_chunking_top_result=top_bad,
            good_chunking_top_result=top_good,
            analysis=analysis_text
        )

        return SearchResponse(
            good_chunks_results=good_results,
            bad_chunks_results=bad_results,
            comparison=comparison
        )

    def answer_query(self, req: RAGRequest) -> RAGResponse:
        query_vec = self.embedder.embed(req.query)
        retrieved_items = self.good_store.similarity_search(query_vec, k=req.top_k)

        answer = self.llm.generate_answer(req.query, retrieved_items)

        return RAGResponse(
            query=req.query,
            answer=answer,
            retrieved_context=retrieved_items,
            model_used=self.llm.model if self.llm.is_configured() else "Local Simulation Mode"
        )

    def simple_ask(self, req: SimpleAskRequest) -> SimpleAnswerResponse:
        """ارسل سؤال واحصل على إجابة نصية واضحة ومباشرة مع مصادرها بحد أقصى سطرين."""
        import re
        raw_q = req.question.strip()
        # تنظيف الحروف المتكررة مثل الوووو أو هلاااا
        clean_q = re.sub(r'(.)\1+', r'\1\1', raw_q.lower()).strip()
        clean_q_single = re.sub(r'(.)\1+', r'\1', raw_q.lower()).strip()
        
        # كشف رسائل التحية والترحيب والنداء
        greetings = [
            "مرحبا", "مرحباً", "اهلا", "أهلا", "أهلاً", "سلام", "السلام عليكم",
            "صباح الخير", "مساء الخير", "هلا", "هاي", "الو", "الوو", "ألو", "ألوو",
            "هلو", "هللو", "يا هلا", "تحياتي", "hi", "hello", "hey", "halo", "allo"
        ]
        
        is_greeting = any(
            clean_q == g or clean_q.startswith(g + " ") or 
            clean_q_single == g or clean_q_single.startswith(g + " ")
            for g in greetings
        )
        
        if is_greeting:
            return SimpleAnswerResponse(
                question=req.question,
                answer="أهلاً وسهلاً بك! كيف يمكنني مساعدتك في الإجابة عن أي استفسار من واقع البيانات واللوائح المتاحة؟",
                sources=[]
            )

        query_vec = self.embedder.embed(req.question)
        retrieved_items = self.good_store.similarity_search(query_vec, k=3)

        # إذا كانت أعلى نتيجة تشابه ضعيفة جداً (سؤال عشوائي أو لا علاقة له بالبيانات)
        max_score = max([item.score for item in retrieved_items], default=0.0)
        if max_score < 0.08 and not self.llm.is_configured():
            return SimpleAnswerResponse(
                question=req.question,
                answer="عذراً، هذا السؤال غير متوفر في اللائحة والبيانات المتاحة. يرجى طرح سؤال متعلق بمحتوى البيانات.",
                sources=[]
            )

        answer = self.llm.generate_answer(req.question, retrieved_items)

        sources = []
        if "غير متوفرة" not in answer and "لم يتم العثور" not in answer:
            for item in retrieved_items:
                title = item.chunk.metadata.get("article_title", "غير محدد")
                if title not in sources:
                    sources.append(title)

        return SimpleAnswerResponse(
            question=req.question,
            answer=answer,
            sources=sources
        )

    def get_health(self) -> HealthResponse:
        model_name = self.embedder.model_name if self.embedder.using_api else f"{self.embedder.model_name} (Active: Built-in Local)"
        return HealthResponse(
            status="healthy",
            indexed_articles=self.articles_count,
            good_chunks_count=len(self.good_store.documents),
            bad_chunks_count=len(self.bad_store.documents),
            openrouter_configured=self.llm.is_configured(),
            embedding_model=model_name,
            embedding_dimensions=self.embedder.last_dimension
        )

