import time
from typing import Dict, Any, List
from app.models.schemas import TranslationRequest, TranslationResponse, EmojiCard, NLPAnalysis
from app.nlp.preprocessor import preprocessor
from app.nlp.analyzer import analyzer
from app.nlp.gloss_generator import gloss_generator
from app.nlp.isl_config import get_sign_language_reorderer, get_emoji_mapper, CURRENT_SIGN_LANGUAGE
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    @staticmethod
    def translate(request: TranslationRequest) -> TranslationResponse:

        start_time = time.time()

        isl_reorderer = get_sign_language_reorderer(CURRENT_SIGN_LANGUAGE)
        isl_emoji_mapper = get_emoji_mapper(CURRENT_SIGN_LANGUAGE)

        logger.info(f"Translating with {CURRENT_SIGN_LANGUAGE} pipeline")

        cleaned_text = preprocessor.clean_text(request.text)

        analysis_result = analyzer.analyze(cleaned_text)

        reordered_data = isl_reorderer.reorder(analysis_result)

        gloss_result = gloss_generator.generate(reordered_data)
        gloss_sequence = gloss_result["gloss_list"]

        mapped_emojis = isl_emoji_mapper.map_gloss(gloss_sequence)

        emoji_display = " ".join([m["emoji"] for m in mapped_emojis])

        emoji_cards = [
            EmojiCard(
                word=m["word"],
                emoji=m["emoji"],
                confidence=m["confidence"],
                method=m["method"],
                alternatives=m["alternatives"],
                lottie_file=m["lottie_file"],

                semantic_role="UNKNOWN"
            )
            for m in mapped_emojis
        ]

        processing_time_ms = int((time.time() - start_time) * 1000)

        analysis_data = NLPAnalysis(
            original_text=request.text,
            is_question=analysis_result["is_question"],
            semantic_roles=analysis_result["semantic_roles"]
        )

        if request.include_details:
            analysis_data.tokens = analysis_result.get("tokens", [])

        isl_metadata = reordered_data.get("isl_metadata", {})
        grammatical_structure = reordered_data.get("grammatical_structure", {})

        logger.info(f"Translation complete in {processing_time_ms}ms (ISL: {CURRENT_SIGN_LANGUAGE})")

        return TranslationResponse(
            original_text=request.text,
            preprocessed_text=cleaned_text,
            gloss_string=reordered_data.get("gloss_string", gloss_result["gloss_string"]),
            emoji_sequence=emoji_cards,
            emoji_display=emoji_display,
            confidence_score=min(m["confidence"] for m in mapped_emojis) if mapped_emojis else 0.0,
            processing_time_ms=processing_time_ms,
            analysis=analysis_data,
            warnings=(
                [f"ISL: {isl_metadata.get('verb_type', 'unknown')} verb type detected"] 
                if isl_metadata else []
            ),

        )

