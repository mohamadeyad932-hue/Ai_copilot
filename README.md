# نظام RAG المتكامل مع FastAPI و ChromaDB و OpenRouter و Docker

مشروع متكامل ومُهيكل وفق مبادئ البرمجة النظيفة (Clean Code Architecture) يقدم خدمات استرجاع المعلومات الدلالي (RAG)، والتخزين المتجهي باستخدام **ChromaDB**، والربط مع نماذج الذكاء الاصطناعي من **OpenRouter API** عبر واجهات **FastAPI** وتغليفه في حاويات **Docker**.

---

## 🏛️ البنية الهيكلية للمشروع (Clean Architecture)

```
c:\Users\eyad\Desktop\copilot_ai\
├── app/
│   ├── __init__.py
│   ├── config.py           # إدارة التكوينات ومتغيرات البيئة (Pydantic Settings)
│   ├── models.py           # نماذج البيانات (Pydantic Schemas)
│   ├── prompts.py          # مستودع نصوص التوجيه (System Prompt & User Prompt)
│   ├── reader.py           # قراءة المستندات وتحليل المواد مع كشف الترميز
│   ├── chunker.py          # التتقطيع الجيد والسيء (Good vs Bad Chunking)
│   ├── embedder.py         # محرك التضمين الدلالي (Semantic Vectorizer)
│   ├── vector_store.py     # مخزن المتجهات باستخدام ChromaDB Persistent Client
│   ├── llm.py              # عميل الاتصال بـ OpenRouter LLM API
│   └── service.py          # منسق الخدمة الرئيسي (RAG Service Orchestrator)
├── main.py                 # تطبيق FastAPI ونقاط الاتصال (REST API)
├── data/
│   └── data.txt            # ملف البيانات الأساسية (مقسّم مادة مادة)
├── vector_db/              # قاعدة بيانات ChromaDB المحفوظة محلياً
├── Dockerfile              # بناء صورة دوكر للمشروع
├── docker-compose.yml      # تشغيل الحاوية بأمر واحد
├── .gitignore              # استبعاد الملفات الحساسة والمؤقتة
├── .dockerignore           # تحسين بناء صورة Docker
├── requirements.txt        # مكتبات بايثون المطلوبة (تتضمن ChromaDB)
├── .env.example            # نموذج متغيرات البيئة
└── README.md               # التوثيق الشامل
```

---

## 📝 نصوص التوجيه (Prompts Repository)

تم فصل نصوص التوجيه في ملف مستقل [`app/prompts.py`](file:///c:/Users/eyad/Desktop/copilot_ai/app/prompts.py):

- **System Prompt (`SYSTEM_PROMPT`):** يوجه الـ LLM للالتزام فقط بسياق المواد المتاحة وذكر رقم المادة المستند عليها.
- **User Prompt (`USER_PROMPT_TEMPLATE`):** قوالب لتأطير سياق المواد المسترجعة وسؤال المستخدم بشكل محكم.

---

## 🗄️ التخزين المتجهي (ChromaDB Integration)

يتم تخزين المتجهات والنصوص والـ Metadata و Document IDs محلياً على القرص في مجلد `vector_db/` باستخدام **ChromaDB (PersistentClient)** مع فهارس `hnsw:space: cosine` لضمان سرعة فائقة في الاسترجاع والبحث الدلالي.

---

## 🔑 ضبط مفتاح OpenRouter API

قم بتعديل ملف `.env` وحط المفتاح الخاص بك:

```env
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

---

## 🚀 طرق التشغيل

### الطريقة 1: التشغيل المحلي المباشر (FastAPI / Uvicorn)

1. **تثبيت التبعيات:**
   ```bash
   pip install -r requirements.txt
   ```

2. **تشغيل سيرفر FastAPI:**
   ```bash
   python main.py
   ```

3. **تصفح التوثيق التفاعلي (Swagger UI):**
   [http://localhost:8000/docs](http://localhost:8000/docs)

---

### الطريقة 2: التشغيل باستخدام Docker Compose

```bash
docker-compose up --build
```
