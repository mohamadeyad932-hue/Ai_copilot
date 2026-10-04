"""
OCR Module — تحليل الصور واستخراج النصوص عبر Vision LLM (OpenRouter API)

يعالج نوعين من الصور:
1. صور تحتوي نصوص (مستندات، لقطات شاشة، جداول) → يستخرج النص كـ Markdown
2. صور عادية (طبيعة، أشخاص، منتجات) → يكتب وصفاً تفصيلياً بالعربية كـ Markdown
"""
import base64
import requests
from app.config import settings


# الصيغ المسموح برفعها
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

# برومبت تقني احترافي لاستخراج النصوص الكاملة وتجنب فلاتر الأمان
IMAGE_ANALYSIS_PROMPT = """You are an advanced, high-precision Optical Character Recognition (OCR) engine.
Your task is to transcribe and extract all text from the provided image accurately and completely into Markdown format.

Instructions:
1. If the image contains text, documents, screenshots, or tables:
   - Perform a full, exact, word-for-word transcription of all visible text in its original language (e.g. Arabic/English).
   - Preserve the document structure using proper Markdown (headers #, ##, lists -, tables, bold/italic).
   - Do not summarize, truncate, or omit any section.
   - Do not include introductory notes or meta-comments. Output only the extracted Markdown content directly.

2. If the image is a diagram or chart:
   - Extract all labels, numbers, and text, and clearly describe the diagram layout in Markdown.

3. If the image is purely a photograph with zero text:
   - Provide a concise description of the image in Arabic under '# وصف الصورة'.

Return clean Markdown only."""


# النماذج المعروفة التي تدعم Vision
KNOWN_VISION_MODELS = [
    "gpt-4o", "gpt-4o-mini", "gpt-4-turbo",
    "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro",
    "claude-3-5-sonnet", "claude-3-haiku", "claude-3-opus",
]


def _get_mime_type(filename: str) -> str:
    """تحديد نوع MIME للصورة بناءً على امتداد الملف."""
    ext = filename.rsplit(".", 1)[-1].lower()
    mime_map = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "gif": "image/gif",
    }
    return mime_map.get(ext, "image/png")


def _is_vision_model(model_name: str) -> bool:
    """
    فحص ما إذا كان النموذج يدعم Vision.
    يفحص بالكلمات المفتاحية المعروفة للنماذج التي تدعم الصور.
    """
    model_lower = model_name.lower()
    vision_keywords = ["4o", "4-turbo", "gemini", "claude-3", "vision", "-vl"]
    return any(keyword in model_lower for keyword in vision_keywords)


def _get_vision_model() -> str:
    """
    الحصول على نموذج يدعم Vision.
    - إذا كان النموذج الحالي يدعم Vision → نستخدمه
    - إذا لا → نستخدم gpt-4o-mini كنموذج احتياطي
    """
    current_model = settings.active_model
    if _is_vision_model(current_model):
        return current_model
    # النموذج الحالي لا يدعم Vision، نستخدم البديل
    return "openai/gpt-4o-mini"


def analyze_image(image_bytes: bytes, filename: str) -> str:
    """
    تحليل صورة واستخراج/وصف محتواها كنص Markdown.
    
    - إذا كانت الصورة تحتوي على نصوص → يستخرجها كـ Markdown منسق
    - إذا كانت صورة عادية → يكتب وصفاً تفصيلياً بالعربية
    
    Args:
        image_bytes: محتوى الصورة كبايتات
        filename: اسم الملف الأصلي
        
    Returns:
        النص بتنسيق Markdown
        
    Raises:
        ValueError: إذا لم يتم تكوين مفتاح API
        RuntimeError: إذا فشل الاتصال بالـ API
    """
    api_key = settings.active_api_key
    if not api_key or api_key == "your_openrouter_api_key_here" or len(api_key) < 10:
        raise ValueError(
            "مفتاح OpenRouter API غير مُعَد. يرجى ضبط OPENROUTER_API_KEY في ملف .env\n"
            "تحليل الصور يتطلب نموذج Vision مثل gpt-4o-mini."
        )

    # تحويل الصورة إلى base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = _get_mime_type(filename)

    # تحديد النموذج المناسب
    vision_model = _get_vision_model()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": settings.openrouter_site_url,
        "X-Title": settings.openrouter_site_name,
        "Content-Type": "application/json",
    }

    payload = {
        "model": vision_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": IMAGE_ANALYSIS_PROMPT,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        },
                    },
                ],
            }
        ],
        "temperature": 0.1,
        "max_tokens": 4096,
    }

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        markdown_text = data["choices"][0]["message"]["content"].strip()

        if not markdown_text:
            raise RuntimeError("النموذج لم يُرجع أي نص من الصورة.")

        print(f"[OCR] ✅ تم تحليل الصورة '{filename}' بنجاح عبر {vision_model}")
        return markdown_text

    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_detail = e.response.json().get("error", {}).get("message", "")
        except Exception:
            error_detail = str(e)

        # إذا كان النموذج لا يدعم Vision، نحاول بالنموذج الاحتياطي
        if "image" in error_detail.lower() or "modality" in error_detail.lower():
            if vision_model != "openai/gpt-4o-mini":
                print(f"[OCR] النموذج {vision_model} لا يدعم الصور، التبديل إلى gpt-4o-mini...")
                payload["model"] = "openai/gpt-4o-mini"
                resp2 = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                resp2.raise_for_status()
                data2 = resp2.json()
                return data2["choices"][0]["message"]["content"].strip()

        raise RuntimeError(f"خطأ من OpenRouter API أثناء تحليل الصورة: {error_detail}")

    except Exception as e:
        raise RuntimeError(f"خطأ أثناء تحليل الصورة: {str(e)}")
