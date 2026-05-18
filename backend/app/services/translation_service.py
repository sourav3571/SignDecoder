import time
from typing import Dict, Any, List
from app.models.schemas import TranslationRequest, TranslationResponse, EmojiCard, NLPAnalysis
from app.nlp.preprocessor import preprocessor
from app.nlp.analyzer import analyzer
from app.nlp.gloss_generator import gloss_generator
from app.nlp.reorderer import reorder_for_sign_language
from app.nlp.emoji_mapper import emoji_mapper

class TranslationService:
    @staticmethod
    def translate(request: TranslationRequest) -> TranslationResponse:
        start_time = time.time()
        
        # 1. Preprocess
        cleaned_text = preprocessor.clean_text(request.text)
        
        # 2. Semantic Analysis
        analysis_result = analyzer.analyze(cleaned_text)
        
        # 3. Grammar Reorder (SVO -> SOV)
        reordered_data = reorder_for_sign_language(analysis_result)
        
        # 4. Gloss Generation
        gloss_result = gloss_generator.generate(reordered_data)
        gloss_sequence = gloss_result["gloss_list"]
        
        # 5. Emoji Mapping
        mapped_emojis = emoji_mapper.map_gloss(gloss_sequence)
        
        # Format emoji display string
        emoji_display = " ".join([m["emoji"] for m in mapped_emojis])
        
        # Format EmojiCard list
        emoji_cards = [
            EmojiCard(
                word=m["word"],
                emoji=m["emoji"],
                confidence=m["confidence"],
                method=m["method"],
                alternatives=m["alternatives"],
                lottie_file=m["lottie_file"],
                # We could extract semantic role by mapping it back, but simplifying here
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
            
        return TranslationResponse(
            original_text=request.text,
            preprocessed_text=cleaned_text,
            gloss_string=gloss_result["gloss_string"],
            emoji_sequence=emoji_cards,
            emoji_display=emoji_display,
            confidence_score=gloss_result["confidence"],
            processing_time_ms=processing_time_ms,
            analysis=analysis_data,
            warnings=["SBERT not loaded. Using exact match fallback."] if "fallback" in [m["method"] for m in mapped_emojis] else []
        )
