import requests
from typing import List
from app.config import settings
from app.models import SearchResultItem
from app.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class OpenRouterLLM:
    """
    عميل الربط مع OpenRouter API لتوليد إجابات دقيقة بناءً على سياق المواد المسترجعة والـ Prompts.
    """
    def __init__(self):
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    @property
    def api_key(self) -> str:
        return settings.active_api_key

    @property
    def model(self) -> str:
        return settings.active_model

    def is_configured(self) -> bool:
        key = self.api_key.strip()
        return bool(key and key != "your_openrouter_api_key_here" and len(key) > 10)

    def generate_answer(self, query: str, context_chunks: List[SearchResultItem]) -> str:
        # صياغة السياق المنسق من المواد
        formatted_context = ""
        
        for idx, item in enumerate(context_chunks, 1):
            title = item.chunk.metadata.get("article_title", f"المادة {idx}")
            formatted_context += f"--- {title} (ID: {item.chunk.id}) ---\n{item.chunk.text}\n\n"

        user_prompt = USER_PROMPT_TEMPLATE.format(
            context=formatted_context.strip(),
            query=query
        )

        if not self.is_configured():
            # بناء إجابة محلية نظيفة من النصوص المسترجعة بدون الحاجة لـ LLM
            if not context_chunks:
                return "لم يتم العثور على معلومات متعلقة بسؤالك في البيانات المتاحة."
            
            answer_parts = ["بناءً على البيانات المتاحة:\n"]
            for idx, item in enumerate(context_chunks, 1):
                title = item.chunk.metadata.get("article_title", f"مصدر {idx}")
                text = item.chunk.text.strip()
                answer_parts.append(f"{idx}. [{title}]: {text}\n")
            
            answer_parts.append("\n(ملاحظة: لتفعيل الإجابة الذكية بالذكاء الاصطناعي، يرجى ضبط OPENROUTER_API_KEY في ملف .env)")
            return "\n".join(answer_parts)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_site_name,
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 200
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"حدث خطأ أثناء الاتصال بـ OpenRouter API: {str(e)}"
