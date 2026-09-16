from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentChunkModel(BaseModel):
    id: str = Field(..., description="المعرف الفريد للقطعة")
    text: str = Field(..., description="نص القطعة المسترجعة")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="البيانات الوصفية (المادة، الاستراتيجية، الطول)")


class SearchQuery(BaseModel):
    query: str = Field(..., example="كم عدد ساعات العمل الرسمية باليوم؟", description="نص سؤال المستخدم")
    top_k: int = Field(default=3, ge=1, le=10, description="عدد القطع المراد استرجاعها")


class SearchResultItem(BaseModel):
    chunk: DocumentChunkModel
    score: float = Field(..., description="درجة تشابه الكوزين (Cosine Similarity Score)")


class ChunkingComparisonResult(BaseModel):
    query: str
    bad_chunking_top_result: Optional[SearchResultItem] = None
    good_chunking_top_result: Optional[SearchResultItem] = None
    analysis: str = Field(..., description="تحليل جودة النتيجة بين التقطيعين")


class SearchResponse(BaseModel):
    good_chunks_results: List[SearchResultItem]
    bad_chunks_results: List[SearchResultItem]
    comparison: ChunkingComparisonResult


class RAGRequest(BaseModel):
    query: str = Field(..., example="كيف يتم حساب أجر العمل الإضافي؟")
    top_k: int = Field(default=3, ge=1, le=10)


class RAGResponse(BaseModel):
    query: str
    answer: str = Field(..., description="الإجابة المولدة بواسطة OpenRouter LLM")
    retrieved_context: List[SearchResultItem] = Field(..., description="السياق المسترجع من المواد")
    model_used: str


class HealthResponse(BaseModel):
    status: str
    indexed_articles: int
    good_chunks_count: int
    bad_chunks_count: int
    openrouter_configured: bool
    embedding_model: str = "built-in"
    embedding_dimensions: int = 1500


class SimpleAskRequest(BaseModel):
    question: str = Field(..., example="كم عدد ساعات العمل الرسمية؟", description="السؤال بنص عربي واضح")


class SimpleAnswerResponse(BaseModel):
    question: str = Field(..., description="السؤال الذي تم طرحه")
    answer: str = Field(..., description="الإجابة النصية الواضحة من البيانات")
    sources: List[str] = Field(default_factory=list, description="المواد المستند عليها في الإجابة")
