# استخدام صورة Python 3.11 خفيفة ومستقرة
FROM python:3.11-slim

# ضبط مجلد العمل داخل الحاوية
WORKDIR /app

# منع بايثون من كتابة ملفات .pyc وإرسال المخرجات مباشرة إلى الـ Terminal بدون تأخير
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# نسخ ملف المتطلبات أولاً للاستفادة من كاش الدوكر
COPY requirements.txt .

# تثبيت الحزم المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع إلى داخل الحاوية
COPY . .

# الأمر الافتراضي لتشغيل السكربت
CMD ["python", "cal_api_llm.py"]
