# JSON Storage Project

مشروع بايثون بسيط لقراءة وحفظ البيانات بصيغة JSON مع معالجة الأخطاء وتنظيم الكود في موديولز.

---

## 🚀 التشغيل السريع

### 1. تفعيل البيئة الافتراضية
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. تثبيت المتطلبات (اختياري)
```bash
pip install -r requirements.txt
```

### 3. تشغيل البرنامج
```bash
python main.py
```

---

## 📁 هيكل المشروع

```text
copilot_ai/
├── data/
│   └── settings.json        # ملف حفظ البيانات
├── storage/
│   ├── __init__.py
│   └── json_handler.py      # دوال قراءة وكتابة الـ JSON
├── main.py                  # نقطة تشغيل التطبيق
├── requirements.txt         # المكتبات
└── .gitignore               # استبعاد ملفات البيئة والكاش
```
