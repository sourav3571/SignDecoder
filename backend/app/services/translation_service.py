import time
import os
import sys
from typing import Dict, Any, List
from app.models.schemas import TranslationRequest, TranslationResponse, EmojiCard, NLPAnalysis
from app.nlp.preprocessor import preprocessor
from app.nlp.analyzer import analyzer
from app.nlp.isl_config import CURRENT_SIGN_LANGUAGE
import logging

# Ensure backend/models/ is on sys.path for emoji_ml imports
_here = os.path.abspath(__file__)
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
_models_dir = os.path.join(_backend_dir, "models")
if _models_dir not in sys.path:
    sys.path.insert(0, _models_dir)

logger = logging.getLogger(__name__)

class TranslationService:
    @staticmethod
    def translate(request: TranslationRequest) -> TranslationResponse:
        start_time = time.time()

        sign_language = request.sign_language or CURRENT_SIGN_LANGUAGE

        if sign_language != "ISL":
            raise ValueError(f"Unsupported sign language: {sign_language}")

        logger.info(f"Translating with {sign_language} pipeline (simple word mapping)")

        cleaned_text = preprocessor.clean_text(request.text)

        # Run semantic analysis to extract tokens
        analysis_result = analyzer.analyze(cleaned_text)
        tokens = analysis_result.get("tokens", [])

        # Simple mapping: convert words to uppercase glosses and drop basic stop words
        _STOP = {
            "a", "an", "the", "is", "am", "are", "was", "were",
            "be", "been", "being", "do", "does", "did", "have",
            "has", "had", "will", "would", "shall", "should",
            "may", "might", "can", "could", "must", "to", "at",
            "in", "on", "from", "with", "by", "about", "for", "of",
            "and", "but", "or", "yet", "so",
        }

        gloss_sequence = []
        if tokens:
            for t in tokens:
                lemma = t.get("lemma", t.get("text", "")).upper()
                if lemma.lower() not in _STOP:
                    gloss_sequence.append(lemma)
        else:
            words = [w.strip(".,!?;:'\"") for w in cleaned_text.lower().split()]
            gloss_sequence = [w.upper() for w in words if w and w not in _STOP]

        # Fallback to keep everything if filtering left it empty
        if not gloss_sequence:
            words = [w.strip(".,!?;:'\"") for w in cleaned_text.lower().split()]
            gloss_sequence = [w.upper() for w in words if w]

        # ── ML-based Emoji Translation ──
        from emoji_ml.inference import EmojiPredictor
        predictor = EmojiPredictor()
        
        gloss_string = " ".join(gloss_sequence)
        prediction = predictor.predict(gloss_string)
        predicted_emoji_str = prediction.get("emoji", "")
        
        # Split predicted emoji string to align 1-to-1 with gloss sequence
        predicted_emoji_tokens = predicted_emoji_str.strip().split()
        
        mapped_emojis = []
        if len(predicted_emoji_tokens) == len(gloss_sequence):
            for i, word in enumerate(gloss_sequence):
                mapped_emojis.append({
                    "word": word,
                    "emoji": predicted_emoji_tokens[i],
                    "confidence": 0.9,
                    "method": "ml-model",
                    "category": "object",
                    "alternatives": [],
                    "lottie_file": None,
                })
        else:
            # If lengths don't match, map word-by-word to guarantee 1-to-1 alignment
            for word in gloss_sequence:
                single_pred = predictor.predict(word)
                single_emoji = single_pred.get("emoji", "❓").strip()
                mapped_emojis.append({
                    "word": word,
                    "emoji": single_emoji if single_emoji else "❓",
                    "confidence": 0.7,
                    "method": "ml-fallback-word",
                    "category": "object",
                    "alternatives": [],
                    "lottie_file": None,
                })

        emoji_display = " ".join([m["emoji"] for m in mapped_emojis])

        # ── Build a word→role reverse lookup from semantic_roles ──
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
        
        # Fallback mapping for common sign language words if NLP fails to assign a role
        _COMMON_WORD_ROLES = {
            # TIME
            "YESTERDAY": "TIME", "TODAY": "TIME", "TOMORROW": "TIME",
            "MORNING": "TIME", "NIGHT": "TIME", "AFTERNOON": "TIME", "EVENING": "TIME",
            "WEEK": "TIME", "YEAR": "TIME", "MONTH": "TIME", "DAILY": "TIME",
            "BEFORE": "TIME", "AFTER": "TIME", "NOW": "TIME", "CLOCK": "TIME",
            "SUMMER": "TIME", "WINTER": "TIME", "RAINY": "TIME",
            # SUBJECTS / PRONOUNS
            "I": "SUBJECT", "YOU": "SUBJECT", "HE": "SUBJECT", "SHE": "SUBJECT",
            "WE": "SUBJECT", "THEY": "SUBJECT", "MY": "SUBJECT", "YOUR": "SUBJECT",
            "HIS": "SUBJECT", "HER": "SUBJECT", "OUR": "SUBJECT", "THEIR": "SUBJECT",
            "ME": "SUBJECT", "US": "SUBJECT", "THEM": "SUBJECT",
            "SOURAV": "SUBJECT", "PRIYA": "SUBJECT", "AMIT": "SUBJECT",
            "VIKRAM": "SUBJECT", "ANJALI": "SUBJECT", "RAHUL": "SUBJECT",
            "NEHA": "SUBJECT", "ARJUN": "SUBJECT", "POOJA": "SUBJECT", "ROHAN": "SUBJECT",
            # NEGATION
            "NOT": "NEGATION", "NEVER": "NEGATION", "NO": "NEGATION", "DONT": "NEGATION",
            "CANT": "NEGATION", "WON T": "NEGATION", "WONT": "NEGATION",
            # VERBS
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
            # LOCATIONS
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
                word_text = token.get("text", "")
                pred = predictor.predict(word_text)
                token["emoji"] = pred.get("emoji", "❓").strip() or "❓"
            analysis_data.tokens = tokens_list

        logger.info(f"Translation complete in {processing_time_ms}ms (ISL: {CURRENT_SIGN_LANGUAGE})")

        return TranslationResponse(
            original_text=request.text,
            preprocessed_text=cleaned_text,
            gloss_string=gloss_string,
            emoji_sequence=emoji_cards,
            emoji_display=emoji_display,
            confidence_score=0.9 if predictor.model_available else 0.7,
            processing_time_ms=processing_time_ms,
            analysis=analysis_data,
            warnings=[]
        )
