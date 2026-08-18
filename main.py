import json
from datetime import datetime
from pathlib import Path
from storage.json_handler import read_json, write_json

DATA_FILE = Path("data/user_data.json")


def main():
    print("=" * 45)
    print("📥 برنامج إدخال وحفظ البيانات بصيغة JSON")
    print("=" * 45)

    # استقبال مدخلات مخصصة من المستخدم
    title = input("اكتب عنواناً أو اسماً للبيانات: ").strip()
    content = input("اكتب أي محتوى أو نص تريد حفظه: ").strip()
    category = input("اكتب تصنيفاً (اختياري - اضغط Enter للتخطي): ").strip()

    # تجهيز كائن البيانات (Dictionary)
    user_record = {
        "title": title if title else "بدون عنوان",
        "content": content if content else "لا يوجد محتوى",
        "category": category if category else "عام",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # قراءة البيانات القديمة إن وجدت لإضافة الإدخال الجديد كقائمة
    existing_data = read_json(DATA_FILE)
    if not isinstance(existing_data, list):
        existing_data = []

    existing_data.append(user_record)

    # 1. الحفظ في ملف JSON
    print("\n⏳ جاري حفظ بياناتك في ملف JSON...")
    if write_json(DATA_FILE, existing_data):
        print(f"✅ تم الحفظ بنجاح داخل: {DATA_FILE}")

    # 2. القراءة والعرض المباشر
    print("\n" + "-" * 45)
    print("📖 قراءة البيانات المحفوظة من الملف وعرضها:")
    print("-" * 45)
    
    saved_data = read_json(DATA_FILE)
    if saved_data:
        # عرض البيانات بتنسيق JSON مقروء وجميل
        formatted_json = json.dumps(saved_data, indent=4, ensure_ascii=False)
        print(formatted_json)
    print("=" * 45)


if __name__ == "__main__":
    main()
