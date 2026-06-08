"""
emoji_routes.py
───────────────
FastAPI router that exposes the ML emoji prediction model via REST.

Endpoint:  POST /api/convert-to-emoji
  • Accepts  { "text": "gloss string" }
  • Returns  { "success": true, "input": "...", "emoji": "👤 🍽️ 🌅", "model": "GlossToEmojiModel" }

Design decisions:
  • Singleton pattern  — model weights are loaded on the FIRST request only,
    not at import / startup time, so the server starts instantly.
  • sys.path patching  — computes the path to backend/models/ relative to
    __file__ so the route works from any working directory.
  • Structured logging — every request logs input length, output emoji count,
    and latency so you can correlate server logs with frontend behaviour.
  • Tiered HTTP errors — 422 (Pydantic, blank text), 503 (model not available),
    500 (inference crash).  Each tier has a distinct log level.

Debug tips:
  • Set LOG_LEVEL=DEBUG in .env to see per-token timing.
  • Watch logs:  Get-Content backend\\logs\\signspeak.log -Wait -Tail 30
  • Swagger UI:  http://localhost:8000/docs#/Emoji%20ML/convert_to_emoji
"""

import sys
import os
import time
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)













_here        = os.path.abspath(__file__)           
_backend_dir = os.path.dirname(              
               os.path.dirname(              
               os.path.dirname(              
               os.path.dirname(_here))))    
_models_dir  = os.path.join(_backend_dir, "models")

logger.debug(f"emoji_routes: resolved backend dir → {_backend_dir}")
logger.debug(f"emoji_routes: adding to sys.path   → {_models_dir}")

if _models_dir not in sys.path:
    sys.path.insert(0, _models_dir)





_predictor = None          
_load_error: Optional[str] = None   


def _get_predictor():
    """
    Return the cached EmojiPredictor instance.

    On the very first call the weights are loaded from disk (can take a few
    seconds on CPU).  All subsequent calls return the cached instance instantly.

    Raises RuntimeError with a human-readable message on failure so the
    route can convert it to a 503 response.
    """
    global _predictor, _load_error

    
    if _predictor is not None:
        return _predictor

    
    if _load_error is not None:
        raise RuntimeError(_load_error)

    logger.info("🤖 [emoji] Lazy-loading ML model — first request, please wait…")
    logger.debug(f"[emoji] sys.path during load: {sys.path[:4]}")
    t0 = time.perf_counter()

    try:
        from emoji_ml.inference import EmojiPredictor  
        _predictor = EmojiPredictor()
        elapsed = time.perf_counter() - t0
        logger.info(f"✓ [emoji] Model loaded in {elapsed:.2f}s — ready for inference")
        logger.info(f"  [emoji] Device  : {getattr(_predictor, 'device', 'unknown')}")
        logger.info(f"  [emoji] Vocab   : {len(getattr(_predictor, 'vocab', []))} tokens")
        return _predictor

    except FileNotFoundError as exc:
        msg = (
            "Emoji ML model weights not found. "
            f"Expected path: {_models_dir}/emoji_ml/saved_model/best_model.pt — "
            "train the model first: cd backend/models/emoji_ml && python train.py"
        )
        logger.error(f"✗ [emoji] {msg}")
        logger.debug(f"[emoji] FileNotFoundError detail: {exc}")
        _load_error = msg
        raise RuntimeError(msg) from exc

    except ImportError as exc:
        msg = (
            f"Could not import emoji_ml — checked path: {_models_dir}. "
            f"Underlying error: {exc}"
        )
        logger.error(f"✗ [emoji] {msg}")
        _load_error = msg
        raise RuntimeError(msg) from exc

    except Exception as exc:
        msg = f"Emoji ML model failed to load: {type(exc).__name__}: {exc}"
        logger.error(f"✗ [emoji] {msg}", exc_info=True)
        _load_error = msg
        raise RuntimeError(msg) from exc






class EmojiRequest(BaseModel):
    """
    Request body for POST /api/convert-to-emoji.

    Fields:
        text (str): English sentence or ISL gloss string.
                    Must be non-empty after stripping whitespace.
                    Will be trimmed before being sent to the model.

    Example:
        { "text": "yesterday home sourav breakfast eat" }
    """
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        """Reject empty / whitespace-only input before it reaches the model."""
        if not v or not v.strip():
            raise ValueError(
                "text field must not be empty or whitespace-only. "
                "Provide a valid English sentence or ISL gloss string."
            )
        return v.strip()


class EmojiResponse(BaseModel):
    """
    Successful response from POST /api/convert-to-emoji.

    Fields:
        success (bool): Always True for 2xx responses.
        input   (str):  The (possibly trimmed) text that was processed.
        emoji   (str):  Space-separated emoji string, e.g. "👤 🍽️ 🌅".
        model   (str):  Name of the underlying ML model.
        tokens  (int):  Number of emoji tokens in the output.

    Example:
        {
          "success": true,
          "input":   "I eat breakfast morning",
          "emoji":   "👤 🥣 🌅 🍽️",
          "model":   "GlossToEmojiModel",
          "tokens":  4
        }
    """
    success: bool = True
    input:   str
    emoji:   str
    model:   str = "GlossToEmojiModel"
    tokens:  int = 0          






router = APIRouter(
    prefix="/api",
    tags=["Emoji ML"],
)


@router.post(
    "/convert-to-emoji",
    response_model=EmojiResponse,
    summary="Convert gloss/text to emoji sequence",
    description="""
Runs the pre-trained **GlossToEmojiModel** (PyTorch Transformer) to convert an
English sentence or ISL gloss string into a space-separated emoji sequence.

**Loading behaviour**: the model is loaded lazily on the *first* call (may
take a few seconds). All subsequent calls return instantly from the cached
instance.

**Common errors**:
| Status | Cause                                   | Fix                            |
|--------|-----------------------------------------|--------------------------------|
| 422    | `text` is empty / missing               | Send a non-empty gloss string  |
| 503    | Model weights not found                 | Run `python train.py` first    |
| 500    | Inference crashed (OOM, CUDA error, …)  | Check server logs              |
""",
    response_description="Emoji sequence generated by the ML model",
)
async def convert_to_emoji(request: EmojiRequest, http_req: Request) -> EmojiResponse:
    """
    POST /api/convert-to-emoji

    Converts a gloss / English text string into an emoji sequence using the
    trained GlossToEmojiModel.

    Args:
        request  : Validated EmojiRequest with a non-blank ``text`` field.
        http_req : FastAPI Request object (used for client IP in debug logs).

    Returns:
        EmojiResponse with success=True, input text, emoji string, and token count.

    Raises:
        HTTPException 503 : Model not loaded (weights missing or load error).
        HTTPException 500 : Inference failure (model crash, OOM, etc.).
    """
    client_ip = http_req.client.host if http_req.client else "unknown"
    logger.info(
        f"📥 [emoji] Request from {client_ip} — "
        f"text[{len(request.text)} chars]: '{request.text[:80]}'"
        + ("…" if len(request.text) > 80 else "")
    )

    
    t_load = time.perf_counter()
    try:
        predictor = _get_predictor()
    except RuntimeError as exc:
        logger.error(f"🚫 [emoji] Model unavailable: {exc}")
        raise HTTPException(
            status_code=503,
            detail=(
                f"{exc}  |  "
                "Ensure backend is started from the backend/ directory and "
                "the trained weights exist at models/emoji_ml/saved_model/best_model.pt"
            ),
        ) from exc

    logger.debug(f"[emoji] Model retrieval took {(time.perf_counter() - t_load)*1000:.1f}ms")

    
    t_infer = time.perf_counter()
    try:
        result: dict = predictor.predict(request.text)
    except Exception as exc:
        logger.error(
            f"💥 [emoji] Inference error for input='{request.text}': "
            f"{type(exc).__name__}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Emoji prediction failed ({type(exc).__name__}): {exc}",
        ) from exc

    infer_ms   = (time.perf_counter() - t_infer) * 1000
    emoji_str  = result.get("emoji", "")
    token_count = len(emoji_str.split()) if emoji_str.strip() else 0

    logger.info(
        f"✅ [emoji] Done in {infer_ms:.0f}ms — "
        f"{token_count} token(s) → '{emoji_str}'"
    )
    logger.debug(f"[emoji] Full predictor output: {result}")

    return EmojiResponse(
        success=True,
        input=result.get("input", request.text),
        emoji=emoji_str,
        tokens=token_count,
    )






@router.get(
    "/emoji-model-status",
    tags=["Emoji ML"],
    summary="Check if the emoji ML model is loaded",
    include_in_schema=True,
)
async def emoji_model_status():
    """
    GET /api/emoji-model-status

    Returns whether the model has been loaded, the cached load error (if any),
    and basic model metadata.  Useful for debugging without triggering a full
    prediction.
    """
    global _predictor, _load_error

    if _predictor is not None:
        return {
            "status": "loaded",
            "model":  "GlossToEmojiModel",
            "device": str(getattr(_predictor, "device", "unknown")),
            "vocab_size": len(getattr(_predictor, "vocab", [])),
            "models_dir": _models_dir,
        }

    if _load_error:
        return {
            "status":     "error",
            "load_error": _load_error,
            "models_dir": _models_dir,
            "hint": "Check backend/logs/ and ensure trained weights exist.",
        }

    return {
        "status":     "not_loaded",
        "models_dir": _models_dir,
        "hint":       "Send a POST /api/convert-to-emoji request to trigger model loading.",
    }


from typing import List, Dict

class ExploreRequest(BaseModel):
    text: str

class ExploreResponse(BaseModel):
    success: bool = True
    query: str
    vector_slice: List[float]
    neighbors: List[Dict]

@router.post(
    "/embeddings/explore",
    response_model=ExploreResponse,
    summary="Explore nearest neighbors in semantic projection space",
)
async def explore_embeddings(request: ExploreRequest) -> ExploreResponse:
    try:
        predictor = _get_predictor()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )
    
    data = predictor.get_embedding_visualization_data(request.text)
    if not data:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve embedding visualization data from model.",
        )
        
    return ExploreResponse(
        success=True,
        query=data["query"],
        vector_slice=data["vector_slice"],
        neighbors=data["neighbors"]
    )
