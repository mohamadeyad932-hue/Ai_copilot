import os
import uvicorn
from fastapi import FastAPI
from app.router import router as ai_router

app = FastAPI(
    title="AI Microservice API",
    description="تطبيق ذكاء اصطناعي محمي ومقسم هيكلياً لتلخيص النصوص واستخراج الكيانات"
)

# تضمين الـ Router الخاص بـ /ai
app.include_router(ai_router)

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8005"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
