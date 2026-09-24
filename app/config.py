import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# تحميل وقراءة ملف .env وتحديث المتغيرات تلقائياً
load_dotenv(override=True)


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_site_url: str = "https://github.com/mohamadeyad932-hue/Ai_copilot"
    openrouter_site_name: str = "RAG Copilot Lab"
    
    # مفتاح LlamaParse API لتحويل PDF إلى Markdown
    llamaparse_api_key: str = ""
    
    # اسم نموذج التضمين (يمكن تغييره بسهولة من .env)
    embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    
    # مجلد تخزين الملفات المرفوعة
    upload_dir: str = "uploads"
    vector_db_dir: str = "vector_db"
    
    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def active_api_key(self) -> str:
        load_dotenv(override=True)
        return os.getenv("OPENROUTER_API_KEY", self.openrouter_api_key).strip()

    @property
    def active_model(self) -> str:
        load_dotenv(override=True)
        return os.getenv("OPENROUTER_MODEL", self.openrouter_model).strip()

    @property
    def active_embedding_model(self) -> str:
        load_dotenv(override=True)
        return os.getenv("EMBEDDING_MODEL_NAME", self.embedding_model_name).strip()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
