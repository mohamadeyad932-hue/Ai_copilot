from typing import List, Optional
from pydantic import BaseModel, Field

class TextRequest(BaseModel):
    text: str = Field(..., min_length=10, description="النص المراد معالجته")

class SummarizeResponse(BaseModel):
    summary: str
    key_points: List[str]

class ExtractedEntity(BaseModel):
    name: str
    category: str = Field(description="مثال: شخص، شركة، تاريخ، موقع")
    details: Optional[str] = None

class ExtractionResponse(BaseModel):
    entities: List[ExtractedEntity]
    topic: str
