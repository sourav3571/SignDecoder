import time
import os
import sys
from typing import Dict, Any, List
from app.models.schemas import TranslationRequest, TranslationResponse, EmojiCard, NLPAnalysis
from app.nlp.preprocessor import preprocessor
from app.nlp.analyzer import analyzer
from app.nlp.isl_config import CURRENT_SIGN_LANGUAGE
import logging


_here = os.path.abspath(__file__)
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
_models_dir = os.path.join(_backend_dir, "models")
if _models_dir not in sys.path:
    sys.path.insert(0, _models_dir)

logger = logging.getLogger(__name__)

GLOSS_TO_EMOJI_HEURISTIC = {
    "I": "👤", "ME": "👤", "MY": "👤", "SELF": "👤",
    "YOU": "👋", "YOUR": "👋", "HE": "👉", "SHE": "👉", "HIM": "👉", "HER": "👉",
    "WE": "👥", "THEY": "👥", "US": "👥", "THEM": "👥",
    "YESTERDAY": "🗓️", "TODAY": "📅", "TOMORROW": "📆",
    "MORNING": "☀️", "NIGHT": "🌙", "AFTERNOON": "🌤️", "EVENING": "🌇",
    "HOME": "🏠", "HOUSE": "🏠", "SCHOOL": "🏫", "OFFICE": "🏢", "HOSPITAL": "🏥",
    "BANK": "🏦", "STORE": "🏪", "PARK": "🌳", "KITCHEN": "🍳",
    "EAT": "😋", "ATE": "😋", "GO": "🏃", "WENT": "🏃", "RUN": "🏃", "PLAY": "⚽",
    "COOK": "🧑‍🍳", "DRINK": "🥛", "SLEEP": "😴", "WALK": "🚶", "DRIVE": "🚗",
    "GIVE": "🤲", "WANT": "🥺", "LIKE": "👍", "LOVE": "❤️", "TAKE": "🤲",
    "SEE": "👁️", "KNOW": "🧠",
    "PIZZA": "🍕", "BURGER": "🍔", "FOOD": "🍕", "WATER": "💧", "MILK": "🥛",
    "FAMILY": "👨‍👩‍👧‍👦", "NO": "❌", "NOT": "❌", "NEVER": "❌", "QUESTION": "🤔",
    "HELLO": "👋", "PLEASE": "🙏", "HAPPY": "😊", "SAD": "😔",
    "BEAUTIFUL": "✨", "NATURE": "🌲",
}


class TranslationService:
    @staticmethod
    def translate(request: TranslationRequest) -> TranslationResponse:
        start_time = time.time()

        sign_language = request.sign_language or CURRENT_SIGN_LANGUAGE

        if sign_language != "ISL":
            raise ValueError(f"Unsupported sign language: {sign_language}")

        logger.info(f"Translating with {sign_language} pipeline (simple word mapping)")

        
        cleaned_text = preprocessor.clean_text(request.text)

        
        
        analysis_result = analyzer.analyze(cleaned_text)
        tokens = analysis_result.get("tokens", [])

        
        from app.nlp.isl_reorderer import isl_reorderer
        reordered_result = isl_reorderer.reorder(analysis_result)
        gloss_sequence = reordered_result.get("reordered_gloss", [])
        
        
        
        if not gloss_sequence:
            _STOP = {
                "a", "an", "the", "is", "am", "are", "was", "were",
                "be", "been", "being", "do", "does", "did", "have",
                "has", "had", "will", "would", "shall", "should",
                "may", "might", "can", "could", "must", "to", "at",
                "in", "on", "from", "with", "by", "about", "for", "of",
                "and", "but", "or", "yet", "so",
            }
            if tokens:
                for t in tokens:
                    lemma = t.get("lemma", t.get("text", "")).upper()
                    if lemma.lower() not in _STOP:
                        gloss_sequence.append(lemma)
            else:
                words = [w.strip(".,!?;:'\"") for w in cleaned_text.lower().split()]
                gloss_sequence = [w.upper() for w in words if w and w not in _STOP]
                if not gloss_sequence:
                    gloss_sequence = [w.upper() for w in words if w]

        
        gloss_string = " ".join(gloss_sequence)
        
        # Initialize predictor early if available
        predictor_available = False
        predictor = None
        try:
            from emoji_ml.inference import EmojiPredictor
            predictor = EmojiPredictor()
            if predictor.model_available:
                predictor_available = True
        except Exception as e:
            logger.warning(f"Failed to load EmojiPredictor: {e}")

        # Determine any OOV words in the input gloss sequence and map them
        oov_replacements = {}
        resolved_gloss_sequence = []
        
        for word in gloss_sequence:
            word_upper = word.upper()
            if word_upper in GLOSS_TO_EMOJI_HEURISTIC:
                resolved_gloss_sequence.append(word_upper)
            else:
                # OOV word, try to find nearest neighbor in vocab
                replaced = False
                if predictor_available and predictor is not None:
                    try:
                        nearest = predictor.find_nearest_glosses(word_upper, k=3)
                        if nearest:
                            top_match = nearest[0]
                            if top_match.get("similarity", 0) >= 0.35:
                                replacement_gloss = top_match["word"].upper()
                                resolved_gloss_sequence.append(replacement_gloss)
                                oov_replacements[word_upper] = {
                                    "replacement": replacement_gloss,
                                    "nearest_neighbors": nearest
                                }
                                replaced = True
                    except Exception as e:
                        logger.error(f"Error resolving OOV word {word_upper} via embeddings: {e}")
                
                if not replaced:
                    resolved_gloss_sequence.append(word_upper)

        # Re-build the gloss string with OOV resolved words
        gloss_string = " ".join(resolved_gloss_sequence)

        # ── STAGE 4: FLAN-T5 model prediction ──
        predicted_emoji_str = ""
        raw_ml_prediction = ""
        semantic_cluster = "NEUTRAL"
        cluster_confidence = 0.5
        
        if predictor_available and predictor is not None:
            try:
                prediction = predictor.predict(gloss_string)
                semantic_cluster = prediction.get("semantic_cluster", "NEUTRAL")
                cluster_confidence = prediction.get("cluster_confidence", 0.5)
                predicted_emoji_str = prediction.get("emoji", "")
                raw_ml_prediction = prediction.get("raw_prediction", "")
            except Exception as e:
                logger.warning(f"Failed to run EmojiPredictor prediction: {e}")

        # Parse the raw ML prediction bracketed tokens to build visual representation cards
        card_sequence = []
        if raw_ml_prediction:
            import re
            ml_tokens = re.findall(r"\[([^\]]+)\]", raw_ml_prediction)
            if not ml_tokens:
                ml_tokens = [t.strip() for t in raw_ml_prediction.split() if t.strip()]
            card_sequence = [t.strip().upper() for t in ml_tokens if t.strip()]
        
        # Fallback to resolved gloss sequence if ML output is empty/missing
        if not card_sequence:
            card_sequence = resolved_gloss_sequence

        mapped_emojis = []
        is_from_ml = bool(raw_ml_prediction)
        
        for word in card_sequence:
            word_upper = word.upper()
            word_lower = word.lower()
            nearest_glosses = []
            
            # Check if this word was a replacement for an OOV word (primarily for fallback/dictionary mapping)
            original_word = word_upper
            is_replacement = False
            for orig_oov, info in oov_replacements.items():
                if info["replacement"] == word_upper:
                    original_word = orig_oov
                    nearest_glosses = info["nearest_neighbors"]
                    is_replacement = True
                    break
            
            single_emoji = ""
            method = "none"
            confidence = 1.0

            # 1. If prediction came from the ML model, map the bracketed token directly to local dictionary
            if is_from_ml and predictor_available and predictor is not None:
                single_emoji = predictor.label_to_emoji.get(word_lower, "")
                if not single_emoji:
                    # Try partial split match (e.g. food_consumption -> food)
                    for key, val in predictor.label_to_emoji.items():
                        if key.split("_")[0] == word_lower:
                            single_emoji = val
                            break
                if single_emoji:
                    mapped_emojis.append({
                        "word": word_upper,
                        "emoji": single_emoji,
                        "confidence": 0.95,
                        "method": "ml-model",
                        "category": "object",
                        "alternatives": [],
                        "lottie_file": None,
                        "nearest_neighbors": None
                    })
                    continue

            # 2. Fallback to normal dictionary lookup & proximity mapping
            if word_upper in GLOSS_TO_EMOJI_HEURISTIC:
                single_emoji = GLOSS_TO_EMOJI_HEURISTIC[word_upper]
                method = "semantic-proximity" if is_replacement else "dictionary-heuristic"
                confidence = 0.95
            else:
                single_emoji = ""
                method = "none"
                confidence = 1.0
                
                # Check semantic proximity
                if predictor_available and predictor is not None:
                    try:
                        nearest = predictor.find_nearest_glosses(word_upper, k=3)
                        if nearest:
                            if not nearest_glosses:
                                nearest_glosses = nearest
                            top_match = nearest[0]
                            if top_match.get("similarity", 0) >= 0.35:
                                single_emoji = top_match["emoji"]
                                method = "semantic-proximity"
                                confidence = round(top_match["similarity"], 2)
                    except Exception as e:
                        logger.error(f"Error in semantic proximity lookup for card {word_upper}: {e}")
                
                # Fallback to individual ML prediction if semantic proximity failed
                if not single_emoji and predictor_available and predictor is not None:
                    try:
                        single_pred = predictor.predict(word)
                        single_emoji = single_pred.get("emoji", "").strip()
                        if single_emoji:
                            # Deduplicate identical consecutive emojis
                            tokens = single_emoji.split()
                            deduped = []
                            for t in tokens:
                                if not deduped or deduped[-1] != t:
                                    deduped.append(t)
                            single_emoji = " ".join(deduped)
                            method = "ml-fallback-word"
                            confidence = 0.7
                    except Exception:
                        pass
            
            mapped_emojis.append({
                "word": original_word,
                "emoji": single_emoji or "❓",
                "confidence": confidence,
                "method": method,
                "category": "object",
                "alternatives": [n["word"] for n in nearest_glosses] if nearest_glosses else [],
                "lottie_file": None,
                "nearest_neighbors": nearest_glosses if nearest_glosses else None
            })

        # Separate out OOV replacements to pass in `oov_sequence` response field
        oov_cards = []
        for orig_oov, info in oov_replacements.items():
            replacement = info["replacement"]
            replacement_emoji = ""
            if predictor_available and predictor is not None:
                replacement_emoji = predictor.label_to_emoji.get(replacement.lower(), "")
                if not replacement_emoji:
                    for key, val in predictor.label_to_emoji.items():
                        if key.split("_")[0] == replacement.lower():
                            replacement_emoji = val
                            break
            if not replacement_emoji:
                replacement_emoji = GLOSS_TO_EMOJI_HEURISTIC.get(replacement, "")
            
            oov_cards.append(
                EmojiCard(
                    word=orig_oov,
                    emoji=replacement_emoji or "❓",
                    confidence=round(info["nearest_neighbors"][0]["similarity"], 2) if info["nearest_neighbors"] else 0.95,
                    method="semantic-proximity",
                    alternatives=[n["word"] for n in info["nearest_neighbors"]] if info["nearest_neighbors"] else [],
                    lottie_file=None,
                    semantic_role="OBJECT",
                    nearest_neighbors=info["nearest_neighbors"]
                )
            )

        emoji_display = " ".join([m["emoji"] for m in mapped_emojis if m["emoji"]])

        
        _ROLE_MAP = {
            "subject": "SUBJECT",
            "verb": "VERB",
            "object": "OBJECT",
            "time": "TIME",
            "location": "LOCATION",
            "negation": "NEGATION",
            "modifier": "OBJECT",
            "indirect_object": "OBJECT",
            "auxiliary": "VERB",
        }
        
        
        _COMMON_WORD_ROLES = {
            
            "YESTERDAY": "TIME", "TODAY": "TIME", "TOMORROW": "TIME",
            "MORNING": "TIME", "NIGHT": "TIME", "AFTERNOON": "TIME", "EVENING": "TIME",
            "WEEK": "TIME", "YEAR": "TIME", "MONTH": "TIME", "DAILY": "TIME",
            "BEFORE": "TIME", "AFTER": "TIME", "NOW": "TIME", "CLOCK": "TIME",
            "SUMMER": "TIME", "WINTER": "TIME", "RAINY": "TIME",
            
            "I": "SUBJECT", "YOU": "SUBJECT", "HE": "SUBJECT", "SHE": "SUBJECT",
            "WE": "SUBJECT", "THEY": "SUBJECT", "MY": "SUBJECT", "YOUR": "SUBJECT",
            "HIS": "SUBJECT", "HER": "SUBJECT", "OUR": "SUBJECT", "THEIR": "SUBJECT",
            "ME": "SUBJECT", "US": "SUBJECT", "THEM": "SUBJECT",
            "SOURAV": "SUBJECT", "PRIYA": "SUBJECT", "AMIT": "SUBJECT",
            "VIKRAM": "SUBJECT", "ANJALI": "SUBJECT", "RAHUL": "SUBJECT",
            "NEHA": "SUBJECT", "ARJUN": "SUBJECT", "POOJA": "SUBJECT", "ROHAN": "SUBJECT",
            
            "NOT": "NEGATION", "NEVER": "NEGATION", "NO": "NEGATION", "DONT": "NEGATION",
            "CANT": "NEGATION", "WON T": "NEGATION", "WONT": "NEGATION",
            
            "EAT": "VERB", "GO": "VERB", "RUN": "VERB", "PLAY": "VERB",
            "COOK": "VERB", "CELEBRATE": "VERB", "TRAVEL": "VERB", "FEEL": "VERB",
            "SEE": "VERB", "LOOK": "VERB", "BUY": "VERB", "WORK": "VERB",
            "STUDY": "VERB", "LIKE": "VERB", "WANT": "VERB", "LOVE": "VERB",
            "HATE": "VERB", "SICK": "VERB", "PASS": "VERB", "FAIL": "VERB",
            "DO": "VERB", "MAKE": "VERB", "TAKE": "VERB", "COME": "VERB",
            "HELP": "VERB", "TELL": "VERB", "ASK": "VERB", "TALK": "VERB",
            "SAY": "VERB", "SPEAK": "VERB", "WRITE": "VERB", "READ": "VERB",
            "DRINK": "VERB", "SLEEP": "VERB", "WALK": "VERB", "DRIVE": "VERB",
            "FLY": "VERB", "RIDE": "VERB", "CLEAN": "VERB", "WASH": "VERB",
            "OPEN": "VERB", "CLOSE": "VERB", "START": "VERB", "STOP": "VERB",
            
            "HOME": "LOCATION", "SCHOOL": "LOCATION", "BANK": "LOCATION",
            "OFFICE": "LOCATION", "SHOP": "LOCATION", "BEACH": "LOCATION",
            "STORE": "LOCATION", "CITY": "LOCATION", "HOSPITAL": "LOCATION",
            "MARKET": "LOCATION", "GARDEN": "LOCATION", "PARK": "LOCATION",
            "ROOM": "LOCATION", "HOUSE": "LOCATION", "KITCHEN": "LOCATION",
            "REST ROOM": "LOCATION", "RESTROOM": "LOCATION", "CLASS": "LOCATION",
            "CLASSROOM": "LOCATION", "UNIVERSITY": "LOCATION", "COLLEGE": "LOCATION",
        }

        semantic_roles = analysis_result.get("semantic_roles", {})
        word_to_role: dict[str, str] = {}
        for role_key, words in semantic_roles.items():
            mapped_role = _ROLE_MAP.get(role_key)
            if not mapped_role:
                continue
            for w in words:
                w_upper = w.upper()
                if w_upper not in word_to_role:
                    word_to_role[w_upper] = mapped_role

        def _resolve_role(word: str) -> str:
            word_upper = word.upper()
            if word_upper in word_to_role:
                return word_to_role[word_upper]
            if word_upper in _COMMON_WORD_ROLES:
                return _COMMON_WORD_ROLES[word_upper]
            return "OBJECT"

        emoji_cards = [
            EmojiCard(
                word=m["word"],
                emoji=m["emoji"],
                confidence=m["confidence"],
                method=m["method"],
                alternatives=m["alternatives"],
                lottie_file=m["lottie_file"],
                semantic_role=_resolve_role(m["word"]),
                nearest_neighbors=m.get("nearest_neighbors"),
            )
            for m in mapped_emojis
        ]

        processing_time_ms = int((time.time() - start_time) * 1000)

        analysis_data = NLPAnalysis(
            original_text=request.text,
            is_question=analysis_result.get("is_question", False),
            semantic_roles=analysis_result.get("semantic_roles", {})
        )

        if request.include_details:
            tokens_list = analysis_result.get("tokens", [])
            for token in tokens_list:
                token["emoji"] = ""
                if predictor_available:
                    try:
                        word_text = token.get("text", "")
                        pred = predictor.predict(word_text)
                        token["emoji"] = pred.get("emoji", "").strip()
                    except Exception:
                        pass
            analysis_data.tokens = tokens_list

        logger.info(f"Translation complete in {processing_time_ms}ms (ISL: {CURRENT_SIGN_LANGUAGE})")

        vector_slice = None
        neighbors = None
        if predictor_available:
            try:
                vis_data = predictor.get_embedding_visualization_data(request.text)
                if vis_data:
                    vector_slice = vis_data.get("vector_slice")
                    neighbors = vis_data.get("neighbors")
            except Exception as e:
                logger.error(f"Error fetching embedding visualization data in TranslationService: {e}")

        return TranslationResponse(
            original_text=request.text,
            preprocessed_text=cleaned_text,
            gloss_string=gloss_string,
            emoji_sequence=emoji_cards,
            emoji_display=emoji_display,
            confidence_score=0.9 if predictor_available else 0.7,
            processing_time_ms=processing_time_ms,
            analysis=analysis_data,
            raw_ml_prediction=raw_ml_prediction if predictor_available else None,
            warnings=[],
            semantic_cluster=semantic_cluster,
            cluster_confidence=cluster_confidence,
            vector_slice=vector_slice,
            neighbors=neighbors,
            oov_sequence=oov_cards
        )

# Trigger reload: Updated OOV mapping synonym booster dictionary v2 (2026-06-07).

