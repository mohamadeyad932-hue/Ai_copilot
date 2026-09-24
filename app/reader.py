"""
PDF Reader — تحويل ملفات PDF إلى Markdown عبر LlamaParse API
"""
import os
import requests
import time
from typing import Optional
from app.config import settings


LLAMAPARSE_UPLOAD_URL = "https://api.cloud.llamaindex.ai/api/parsing/upload"
LLAMAPARSE_STATUS_URL = "https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}"
LLAMAPARSE_RESULT_URL = "https://api.cloud.llamaindex.ai/api/parsing/job/{job_id}/result/markdown"


def convert_pdf_to_markdown(pdf_path: str) -> str:
    """
    رفع ملف PDF إلى LlamaParse API وتحويله إلى Markdown.
    
    Args:
        pdf_path: المسار المحلي لملف PDF
        
    Returns:
        النص بتنسيق Markdown
    """
    api_key = settings.llamaparse_api_key
    if not api_key or len(api_key) < 10:
        raise ValueError("مفتاح LlamaParse API غير مُعَد. يرجى ضبط LLAMAPARSE_API_KEY في ملف .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
    }

    # رفع الملف
    with open(pdf_path, "rb") as f:
        files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
        data = {
            "language": "ar",
            "parsing_instruction": "Extract all text preserving headings and structure as Markdown with Arabic support.",
        }
        resp = requests.post(LLAMAPARSE_UPLOAD_URL, headers=headers, files=files, data=data, timeout=60)
        resp.raise_for_status()
        job_info = resp.json()

    job_id = job_info.get("id")
    if not job_id:
        raise RuntimeError(f"لم يتم الحصول على job_id من LlamaParse: {job_info}")

    # انتظار اكتمال المعالجة
    status_url = LLAMAPARSE_STATUS_URL.format(job_id=job_id)
    for _ in range(120):  # 120 محاولة × 2 ثانية = 4 دقائق كحد أقصى
        time.sleep(2)
        status_resp = requests.get(status_url, headers=headers, timeout=20)
        status_resp.raise_for_status()
        status_data = status_resp.json()
        status = status_data.get("status", "")

        if status == "SUCCESS":
            break
        elif status in ("ERROR", "FAILED"):
            raise RuntimeError(f"فشلت معالجة الملف في LlamaParse: {status_data}")
    else:
        raise TimeoutError("انتهت مهلة الانتظار لمعالجة الملف في LlamaParse (4 دقائق).")

    # جلب النتيجة بتنسيق Markdown
    result_url = LLAMAPARSE_RESULT_URL.format(job_id=job_id)
    result_resp = requests.get(result_url, headers=headers, timeout=30)
    result_resp.raise_for_status()
    result_data = result_resp.json()

    markdown_text = result_data.get("markdown", "")
    if not markdown_text:
        raise RuntimeError("لم يتم استلام نص Markdown من LlamaParse.")

    return markdown_text


def convert_pdf_bytes_to_markdown(pdf_bytes: bytes, filename: str = "document.pdf") -> str:
    """
    تحويل بايتات PDF إلى Markdown عبر LlamaParse API.
    
    Args:
        pdf_bytes: محتوى ملف PDF كبايتات
        filename: اسم الملف الأصلي
        
    Returns:
        النص بتنسيق Markdown
    """
    api_key = settings.llamaparse_api_key
    if not api_key or len(api_key) < 10:
        raise ValueError("مفتاح LlamaParse API غير مُعَد. يرجى ضبط LLAMAPARSE_API_KEY في ملف .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
    }

    files = {"file": (filename, pdf_bytes, "application/pdf")}
    data = {
        "language": "ar",
        "parsing_instruction": "Extract all text preserving headings and structure as Markdown with Arabic support.",
    }
    resp = requests.post(LLAMAPARSE_UPLOAD_URL, headers=headers, files=files, data=data, timeout=60)
    resp.raise_for_status()
    job_info = resp.json()

    job_id = job_info.get("id")
    if not job_id:
        raise RuntimeError(f"لم يتم الحصول على job_id من LlamaParse: {job_info}")

    # انتظار اكتمال المعالجة
    status_url = LLAMAPARSE_STATUS_URL.format(job_id=job_id)
    for _ in range(120):
        time.sleep(2)
        status_resp = requests.get(status_url, headers=headers, timeout=20)
        status_resp.raise_for_status()
        status_data = status_resp.json()
        status = status_data.get("status", "")

        if status == "SUCCESS":
            break
        elif status in ("ERROR", "FAILED"):
            raise RuntimeError(f"فشلت معالجة الملف في LlamaParse: {status_data}")
    else:
        raise TimeoutError("انتهت مهلة الانتظار لمعالجة الملف في LlamaParse (4 دقائق).")

    # جلب النتيجة بتنسيق Markdown
    result_url = LLAMAPARSE_RESULT_URL.format(job_id=job_id)
    result_resp = requests.get(result_url, headers=headers, timeout=30)
    result_resp.raise_for_status()
    result_data = result_resp.json()

    markdown_text = result_data.get("markdown", "")
    if not markdown_text:
        raise RuntimeError("لم يتم استلام نص Markdown من LlamaParse.")

    return markdown_text
