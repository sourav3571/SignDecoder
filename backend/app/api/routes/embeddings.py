"""
GET /api/v1/embeddings/compare?word1=jolly&word2=happy
Returns the raw sentence-transformer embedding vectors for two words
and the cosine similarity between them. Used for the frontend
embedding visualization widget.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/embeddings", tags=["Embeddings"])


@router.get("/compare")
async def compare_embeddings(
    word1: str = Query(..., description="Input / OOV word"),
    word2: str = Query(..., description="Predicted / matched word"),
):
    """
    Returns the SentenceTransformer embedding vectors for `word1` and `word2`
    (first 48 dims, normalised to [−1, 1]) plus their cosine similarity.
    The frontend uses this to render a side-by-side bar chart.
    """
    try:
        import sys, os
        # Make sure the models directory is importable
        models_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "models")
        models_dir = os.path.normpath(models_dir)
        if models_dir not in sys.path:
            sys.path.insert(0, models_dir)

        from emoji_ml.inference import EmojiPredictor
        import torch
        import torch.nn.functional as F

        predictor = EmojiPredictor()
        if predictor.emb_model is None:
            raise HTTPException(status_code=503, detail="Embedding model not loaded")

        # Encode both words
        words = [word1.lower(), word2.lower()]
        embs = predictor.emb_model.encode(words, convert_to_tensor=True)  # (2, 384)
        embs_norm = F.normalize(embs, p=2, dim=-1)

        # Cosine similarity
        sim = torch.dot(embs_norm[0], embs_norm[1]).item()

        # Slice to first 48 dims for compact visualisation
        vec1 = embs_norm[0, :48].tolist()
        vec2 = embs_norm[1, :48].tolist()

        # Also compute projected (semantic space) vectors if available
        proj_vec1: List[float] = []
        proj_vec2: List[float] = []
        proj_sim: float | None = None

        if predictor.clustering_available and predictor.projected_embeddings is not None:
            try:
                with torch.no_grad():
                    pv1 = F.normalize(predictor.projection_net(embs[0].unsqueeze(0)), p=2, dim=-1)
                    pv2 = F.normalize(predictor.projection_net(embs[1].unsqueeze(0)), p=2, dim=-1)
                proj_sim = torch.dot(pv1.squeeze(0), pv2.squeeze(0)).item()
                proj_vec1 = pv1.squeeze(0)[:48].tolist()
                proj_vec2 = pv2.squeeze(0)[:48].tolist()
            except Exception as e:
                logger.warning(f"Projection failed: {e}")

        return {
            "word1": word1,
            "word2": word2,
            "cosine_similarity": round(sim, 4),
            "projected_similarity": round(proj_sim, 4) if proj_sim is not None else None,
            "vec1": [round(v, 4) for v in vec1],
            "vec2": [round(v, 4) for v in vec2],
            "proj_vec1": [round(v, 4) for v in proj_vec1],
            "proj_vec2": [round(v, 4) for v in proj_vec2],
            "dims": 48,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Embedding compare error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
