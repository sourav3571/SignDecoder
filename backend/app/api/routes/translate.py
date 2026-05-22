from fastapi import APIRouter, HTTPException
from app.models.schemas import TranslationRequest, TranslationResponse, BatchTranslationRequest, BatchTranslationResponse
from app.services.translation_service import TranslationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/translate", tags=["Translation"])

@router.post("", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):

    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty.")

        return TranslationService.translate(request)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=BatchTranslationResponse)
async def translate_batch(request: BatchTranslationRequest):

    results = []
    for text in request.texts:
        if text and len(text.strip()) > 0:
            try:

                req = TranslationRequest(text=text)
                res = TranslationService.translate(req)
                results.append(res)
            except Exception as e:
                logger.error(f"Batch Translation error for '{text}': {e}")

    return BatchTranslationResponse(results=results)
