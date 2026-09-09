from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from openai import APIError, RateLimitError, APITimeoutError

from app.schemas import TextRequest, SummarizeResponse, ExtractionResponse
from app.prompts import (
    SUMMARIZE_SYSTEM_PROMPT, SUMMARIZE_USER_TEMPLATE,
    EXTRACT_SYSTEM_PROMPT, EXTRACT_USER_TEMPLATE
)
from app.ai_service import call_llm_structured

router = APIRouter(prefix="/ai", tags=["AI Operations"])

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(payload: TextRequest):
    user_prompt = SUMMARIZE_USER_TEMPLATE.format(text=payload.text)
    
    try:
        result = call_llm_structured(
            system_prompt=SUMMARIZE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=SummarizeResponse
        )
        return result

    except APITimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="تجاوز الطلب الحد الزمني المسموح به (Timeout)."
        )
    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="تم تجاوز حد الطلبات المسموح به (Rate Limit)، يرجى المحاولة لاحقاً."
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"فشل الـ Validation لاستجابة النموذج: {e.errors()}"
        )
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في المزود: {str(e)}"
        )


@router.post("/extract", response_model=ExtractionResponse)
async def extract_data(payload: TextRequest):
    user_prompt = EXTRACT_USER_TEMPLATE.format(text=payload.text)
    
    try:
        result = call_llm_structured(
            system_prompt=EXTRACT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ExtractionResponse
        )
        return result

    except APITimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="تجاوز الطلب الحد الزمني المسموح به (Timeout)."
        )
    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="تم تجاوز حد الطلبات المسموح به (Rate Limit)."
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"فشل الـ Validation لاستجابة النموذج: {e.errors()}"
        )
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطأ في المزود: {str(e)}"
        )
