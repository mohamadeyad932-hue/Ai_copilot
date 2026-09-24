# RAG Copilot API v3.0

تطبيق RAG (Retrieval-Augmented Generation) للإجابة عن الأسئلة بدقة من مستندات PDF المرفوعة عبر الذكاء الاصطناعي.

## 🚀 كيف يعمل؟

```
رفع PDF → تحويل إلى Markdown (LlamaParse) → تقطيع ذكي → تضمين وفهرسة → اسأل أي سؤال
```

### تقنيات التقطيع الذكي

1. **التقطيع حسب العناوين (MarkdownHeaderTextSplitter)**
   - يمسح النص سطراً بسطر ويكتشف العناوين (#, ##, ###)
   - يفرز كل فقرة تحت عنوانها
   - يُخزن شجرة العناوين في البيانات الوصفية (Metadata) لكل قطعة

2. **حقن السياق (Context Injection)**
   - يضيف مسار العناوين كبادئة لكل قطعة نصية
   - قبل: `السعر: 50 دولار`
   - بعد: `[المنتجات > الهواتف > آيفون 13] السعر: 50 دولار`
   - يحول الـ Vector إلى تمثيل دلالي دقيق ولا يفقد معناه

## 📦 التثبيت

```bash
pip install -r requirements.txt
```

## ⚙️ الإعدادات

أنشئ ملف `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
EMBEDDING_MODEL_NAME=openai/text-embedding-3-large
LLAMAPARSE_API_KEY=your_llamaparse_api_key_here
VECTOR_DB_DIR=vector_db
UPLOAD_DIR=uploads
HOST=0.0.0.0
PORT=8000
```

## 🏃 التشغيل

```bash
python main.py
```

ثم افتح: http://localhost:8000/docs

## 🔗 الـ Endpoints

| Method | Endpoint | الوصف |
|--------|----------|-------|
| `POST` | `/api/upload` | رفع ملف PDF للتحويل والفهرسة |
| `POST` | `/api/ask` | إرسال سؤال والحصول على إجابة |
| `GET` | `/api/health` | فحص حالة النظام |
| `POST` | `/api/clear` | مسح جميع البيانات المفهرسة |

## 📝 أمثلة الاستخدام

### رفع ملف PDF
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf"
```

### طرح سؤال
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "ما هي ساعات العمل الرسمية؟"}'
```
