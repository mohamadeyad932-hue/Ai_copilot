import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

# قراءة إعدادات المفتاح و OpenRouter Base URL من البيئة
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or "your-api-key-here"
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
TIMEOUT = float(os.getenv("AI_TIMEOUT_SECONDS", "15.0"))

# إعداد عميل OpenAI المتوافق مع OpenRouter
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    timeout=TIMEOUT,
    default_headers={
        "HTTP-Referer": "http://localhost:8005",
        "X-Title": "AI Copilot Service"
    }
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RateLimitError, APITimeoutError, ValidationError)),
    reraise=True
)
def call_llm_structured(system_prompt: str, user_prompt: str, response_model):
    """استدعاء النموذج عبر OpenRouter مع إلزام النتيجة بهيكل Pydantic محدد."""
    response = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=response_model,
        temperature=0.2
    )
    return response.choices[0].message.parsed
