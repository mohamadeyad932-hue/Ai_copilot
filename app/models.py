from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentChunkModel(BaseModel):
    id: str = Field(..., description="المعرف الفريد للقطعة")
    text: str = Field(..., description="نص القطعة المسترجعة (مع السياق المحقون)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="البيانات الوصفية (شجرة العناوين، الاستراتيجية، الطول)")


class SearchResultItem(BaseModel):
    chunk: DocumentChunkModel
    score: float = Field(..., description="درجة تشابه الكوزين (Cosine Similarity Score)")


class HealthResponse(BaseModel):
    status: str
    documents_indexed: int = Field(default=0, description="عدد المستندات المفهرسة")
    total_chunks: int = Field(default=0, description="إجمالي القطع في المخزن المتجهي")
    openrouter_configured: bool
    llamaparse_configured: bool
    embedding_model: str = "built-in"
    embedding_dimensions: int = 1500


class SimpleAskRequest(BaseModel):
    question: str = Field(..., example="كم عدد ساعات العمل الرسمية؟", description="السؤال بنص عربي واضح")


class SimpleAnswerResponse(BaseModel):
    question: str = Field(..., description="السؤال الذي تم طرحه")
    answer: str = Field(..., description="الإجابة النصية الواضحة من المستندات")
    sources: List[str] = Field(default_factory=list, description="الأقسام المستند عليها في الإجابة")


class UploadResponse(BaseModel):
    message: str = Field(..., description="رسالة النتيجة")
    filename: str = Field(..., description="اسم الملف المرفوع")
    chunks_count: int = Field(..., description="عدد القطع المنتجة")
    markdown_preview: str = Field(default="", description="معاينة لأول 500 حرف من Markdown")
