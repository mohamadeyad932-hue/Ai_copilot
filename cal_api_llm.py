import os
from google import genai
from dotenv import load_dotenv

# 1. تحميل متغيرات البيئة من ملف .env
load_dotenv()

# 2. إنشاء العميل (سيعتمد تلقائياً على GEMINI_API_KEY من ملف .env)
client = genai.Client()

# 3. إعداد النص المدخل (Prompt)
prompt_text = "ما هي أهداف الذكاء الاصطناعي في تحليل البيانات؟ اجب في سطرين."

print("جاري إرسال الطلب إلى النموذج...")

# 4. تنفيذ استدعاء الـ API
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_text,
)

# 5. طباعة النتيجة
print("\n--- النتيجة ---")
print(response.text)
usage = response.usage_metadata
print("\n--- سجل الاستهلاك (Token Usage) ---")
print(f"Input Tokens:  {usage.prompt_token_count}")
print(f"Output Tokens: {usage.candidates_token_count}")
print(f"Total Tokens:  {usage.total_token_count}")