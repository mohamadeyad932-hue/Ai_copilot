import logging
import time
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import HealthCheckResponse, TextAnalysisRequest, TextAnalysisResponse

# Configure structured logger
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("backend_api")

# Record start time for uptime tracking
START_TIME = time.time()

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Week 2: Backend API Fundamentals - High-performance RESTful API with validation, middleware, and text analysis."
)

# Optional CORS middleware for broad client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_and_log_middleware(request: Request, call_next: Callable) -> Response:
    """
    Custom HTTP middleware to calculate request execution time in milliseconds,
    attach X-Process-Time-Ms header, and output structured logs.
    """
    start_perf = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_perf) * 1000  # Convert to ms

    # Attach response header
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"

    # Structured log output
    logger.info(
        f"Method={request.method} | Path={request.url.path} | Status={response.status_code} | Duration={process_time:.2f}ms"
    )
    return response


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Check API Service Health Status"
)
async def health_check() -> HealthCheckResponse:
    """
    Returns application health status, version, and operational uptime.
    """
    uptime = round(time.time() - START_TIME, 2)
    return HealthCheckResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        uptime_seconds=uptime
    )


@app.post(
    "/api/v1/analyze-text",
    response_model=TextAnalysisResponse,
    status_code=status.HTTP_200_OK,
    tags=["Text Metrics"],
    summary="Perform non-AI text metrics analysis"
)
async def analyze_text(request_data: TextAnalysisRequest) -> TextAnalysisResponse:
    """
    Analyzes input text and returns metrics:
    - Character count
    - Word count
    - Line count
    - Uppercase transformation
    - Alphanumeric validation
    - Estimated reading time (minutes)
    """
    raw_text = request_data.text

    # Handling empty or whitespace-only text with 400 Bad Request
    if not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty or contain only whitespace."
        )

    char_count = len(raw_text)
    words = raw_text.split()
    word_count = len(words)
    lines = raw_text.splitlines()
    line_count = len(lines) if lines else 1
    uppercase_text = raw_text.upper()

    # Determine alphanumeric status (excluding whitespace/punctuation if evaluated strictly, or standard string isalnum)
    # Checking if text (without spaces/newlines) is alphanumeric
    clean_text_no_whitespace = "".join(raw_text.split())
    is_alphanumeric = clean_text_no_whitespace.isalnum() if clean_text_no_whitespace else False

    # Estimated reading time based on standard 200 Words Per Minute (WPM)
    estimated_reading_time = round(word_count / 200.0, 2)

    return TextAnalysisResponse(
        char_count=char_count,
        word_count=word_count,
        line_count=line_count,
        uppercase_text=uppercase_text,
        is_alphanumeric=is_alphanumeric,
        estimated_reading_time_minutes=estimated_reading_time
    )
