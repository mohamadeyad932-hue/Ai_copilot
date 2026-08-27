from pydantic import BaseModel, Field, ConfigDict


class HealthCheckResponse(BaseModel):
    """Schema for service health check response."""
    status: str = Field(..., description="Service status indicator")
    app_name: str = Field(..., description="Name of the application")
    version: str = Field(..., description="Application semantic version")
    uptime_seconds: float = Field(..., description="System uptime in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "app_name": "Backend API Fundamentals",
                "version": "1.0.0",
                "uptime_seconds": 12.34
            }
        }
    )


class TextAnalysisRequest(BaseModel):
    """Schema for text analysis request payload."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The text to analyze (1 to 10,000 characters)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "Hello world! FastAPI is fast and easy to use."
            }
        }
    )


class TextAnalysisResponse(BaseModel):
    """Schema for text analysis result metrics."""
    char_count: int = Field(..., description="Total character count including spaces")
    word_count: int = Field(..., description="Total word count")
    line_count: int = Field(..., description="Total number of lines")
    uppercase_text: str = Field(..., description="The input text transformed to uppercase")
    is_alphanumeric: bool = Field(..., description="Whether the text contains only alphanumeric characters (excluding spaces/punctuation)")
    estimated_reading_time_minutes: float = Field(..., description="Estimated reading time in minutes (based on 200 WPM)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "char_count": 45,
                "word_count": 8,
                "line_count": 1,
                "uppercase_text": "HELLO WORLD! FASTAPI IS FAST AND EASY TO USE.",
                "is_alphanumeric": False,
                "estimated_reading_time_minutes": 0.04
            }
        }
    )
