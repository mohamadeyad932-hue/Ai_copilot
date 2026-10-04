from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.service import RAGService
from app.models import (
    HealthResponse,
    SimpleAskRequest,
    SimpleAnswerResponse,
    UploadResponse,
)

rag_service = RAGService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 السيرفر جاهز — في انتظار رفع ملفات PDF للفهرسة.")
    yield
    print("جاري إغلاق السيرفر...")


app = FastAPI(
    title="RAG Copilot API",
    description="تطبيق RAG للإجابة عن الأسئلة بدقة من مستنداتك PDF عبر الذكاء الاصطناعي.",
    version="3.0.0",
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
        "version": "3.1.0",
        "description": "ارفع ملف PDF أو صورة (PNG/JPG/WEBP) → يتحول إلى Markdown → يتم تقطيعه ذكياً → اسأل أي سؤال",
        "endpoints": {
            "upload": "POST /api/upload  (ارفع ملف PDF أو صورة للفهرسة)",
            "ask": "POST /api/ask  (ارسل سؤالك -> إجابة واضحة ومباشرة)",
            "health": "GET /api/health",
            "clear": "POST /api/clear  (مسح جميع البيانات المفهرسة)"
        },
        "supported_formats": ["PDF", "PNG", "JPG", "JPEG", "WEBP", "GIF"],
        "docs": "/docs",
        "status": "online"
    }


@app.post("/api/upload", response_model=UploadResponse, tags=["Upload"])
async def upload_file(file: UploadFile = File(..., description="ملف PDF أو صورة (PNG, JPG, WEBP) للرفع والفهرسة")):
    """
    رفع ملف PDF أو صورة لتحويله إلى Markdown وتقطيعه وفهرسته.
    
    الصيغ المدعومة:
    - PDF: يتم تحويله عبر LlamaParse API
    - صور (PNG, JPG, JPEG, WEBP, GIF): يتم تحليلها عبر Vision LLM
    
    في كلتا الحالتين:
    1. يتم تحويل المحتوى إلى Markdown
    2. يتم تقطيعه ذكياً حسب العناوين مع حقن السياق
    3. يتم تضمينه وفهرسته في المخزن المتجهي
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="اسم الملف مفقود.")
    
    filename_lower = file.filename.lower()
    is_pdf = filename_lower.endswith(".pdf")
    is_image = any(filename_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"))
    
    if not is_pdf and not is_image:
        raise HTTPException(
            status_code=400,
            detail="صيغة غير مدعومة. الصيغ المسموحة: PDF, PNG, JPG, JPEG, WEBP, GIF"
        )
    
    try:
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="الملف فارغ.")
        
        if is_pdf:
            result = rag_service.process_uploaded_pdf(file_bytes, file.filename)
        else:
            result = rag_service.process_uploaded_image(file_bytes, file.filename)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ أثناء معالجة الملف: {str(e)}")


@app.post("/api/ask", response_model=SimpleAnswerResponse, tags=["Ask"])
def ask_question(request: SimpleAskRequest):
    """
    ارسل سؤالك واحصل على إجابة نصية واضحة ومباشرة من المستندات المرفوعة.
    
    المدخل: { "question": "سؤالك هنا" }
    المخرج: إجابة نصية واضحة + الأقسام المصدرية
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="يرجى إدخال سؤال.")
    return rag_service.simple_ask(request)


@app.get("/api/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """فحص حالة النظام والمخازن المتجهية وإعدادات الخدمات."""
    return rag_service.get_health()


@app.post("/api/clear", tags=["Admin"])
def clear_index():
    """مسح جميع البيانات المفهرسة من المخزن المتجهي."""
    result = rag_service.clear_index()
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
