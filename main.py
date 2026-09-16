from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.service import RAGService
from app.models import (
    HealthResponse,
    SimpleAskRequest,
    SimpleAnswerResponse
)

rag_service = RAGService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("جاري تهيئة وفهرسة بيانات المواد...")
    try:
        res = rag_service.initialize_and_index()
        print(f"تمت الفهرسة بنجاح: {res}")
    except Exception as e:
        print(f"خطأ أثناء الفهرسة التلقائية: {e}")
    yield
    print("جاري إغلاق السيرفر...")


app = FastAPI(
    title="RAG Copilot API",
    description="تطبيق RAG للإجابة عن الأسئلة بدقة من بياناتك عبر الذكاء الاصطناعي.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
def root():
    """نقطة الدخول الرئيسية للـ API."""
    return {
        "service": "RAG Copilot API",
        "version": "2.0.0",
        "endpoints": {
            "ask": "POST /api/ask  (ارسل سؤالك -> إجابة واضحة ومباشرة)",
            "health": "GET /api/health",
            "reindex": "POST /api/reindex"
        },
        "docs": "/docs",
        "status": "online"
    }


@app.post("/api/ask", response_model=SimpleAnswerResponse, tags=["Ask"])
def ask_question(request: SimpleAskRequest):
    """
    ارسل سؤالك واحصل على إجابة نصية واضحة ومباشرة من البيانات.
    
    المدخل: { "question": "سؤالك هنا" }
    المخرج: إجابة نصية واضحة + المواد المستند عليها
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="يرجى إدخال سؤال.")
    return rag_service.simple_ask(request)


@app.get("/api/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """فحص حالة النظام والمخازن المتجهية وإعدادات OpenRouter."""
    return rag_service.get_health()


@app.post("/api/reindex", tags=["Admin"])
def reindex_data():
    """إعادة بناء وقراءة الفهرس من ملف data/data.txt."""
    res = rag_service.initialize_and_index()
    return {"message": "تمت إعادة الفهرسة بنجاح", "details": res}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)

