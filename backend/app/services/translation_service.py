import time
import os
import sys
import re
import logging
from app.models.schemas import TranslationRequest, TranslationResponse, EmojiCard, NLPAnalysis
from app.nlp.isl_config import CURRENT_SIGN_LANGUAGE

_here = os.path.abspath(__file__)
_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
_models_dir = os.path.join(_backend_dir, "models")
if _models_dir not in sys.path:
    sys.path.insert(0, _models_dir)

logger = logging.getLogger(__name__)

# Emoji lookup for gloss words
GLOSS_TO_EMOJI = {
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
    "BEAUTIFUL": "✨", "NATURE": "🌲", "CRICKET": "🏏", "GROUND": "🌍",
    "RAVI": "👤", "PLAYING": "⚽", "WHY": "🤔", "WHAT": "🤔", "WHERE": "📍",
}


_simplifier_instance = None

def get_simplifier():
    global _simplifier_instance
    if _simplifier_instance is None:
        import os
        import sys
        import torch
        
        # Save original CWD
        original_cwd = os.getcwd()
        
        # Resolve paths
        _here = os.path.abspath(__file__)
        _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
        lexical_dir = os.path.join(os.path.dirname(_backend_dir), "model for lexical simplification")
        
        if lexical_dir not in sys.path:
            sys.path.insert(0, lexical_dir)
            
        os.chdir(lexical_dir)
        try:
            from ai_simplifier import AILexicalSimplifier
            config = {
                'bert_model': 'bert-base-uncased',
                'max_bert_tokens': 128,
                'lex_mturk_path': 'lex_mturk.txt',
                'benchls_path': 'BenchLS.txt',
                'ppdb_path': 'ppdb_fallback.json',
            }
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info("Initializing AILexicalSimplifier...")
            _simplifier_instance = AILexicalSimplifier(config, device)
            logger.info("AILexicalSimplifier initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize AILexicalSimplifier: {e}")
            raise e
        finally:
            os.chdir(original_cwd)
            
    return _simplifier_instance


class TranslationService:
    @staticmethod
    def translate(request: TranslationRequest) -> TranslationResponse:
        start_time = time.time()

        sign_language = request.sign_language or CURRENT_SIGN_LANGUAGE
        if sign_language != "ISL":
            raise ValueError(f"Unsupported sign language: {sign_language}")

        # ── Step 0: Run Lexical Simplification if requested ───────────────────
        preprocessed_text = request.text
        warnings = []
        if getattr(request, 'simplify', False):
            try:
                simplifier = get_simplifier()
                preprocessed_text = simplifier.simplify(request.text, verbose=False)
                logger.info(f"Lexically simplified: '{request.text}' → '{preprocessed_text}'")
                if preprocessed_text.lower().strip() != request.text.lower().strip():
                    warnings.append(f"Lexically simplified input from: '{request.text}'")
            except Exception as e:
                logger.error(f"Lexical simplification failed: {e}")
                warnings.append(f"Simplification error: {str(e)}")

        # ── Step 1: Run the model — input → gloss ──────────────────────────────
        gloss_string = ""
        try:
            from emoji_ml.gloss_model_use import generate_pos_tags, translate_to_isl
            pos_tags = generate_pos_tags(preprocessed_text)
            isl_input = preprocessed_text + " | " + pos_tags
            gloss_string = translate_to_isl(isl_input).strip()
            logger.info(f"Model gloss output: '{gloss_string}'")
        except Exception as e:
            logger.warning(f"Gloss model failed: {e}")
            gloss_string = preprocessed_text  # raw fallback

        # ── Step 2: Split gloss into words and map to emojis ───────────────────
        gloss_words = [w.strip(".,!?;:'\"") for w in gloss_string.split() if w.strip(".,!?;:'\"")]

        emoji_cards = []
        for word in gloss_words:
            word_upper = word.upper()
            emoji = GLOSS_TO_EMOJI.get(word_upper, "❓")
            emoji_cards.append(EmojiCard(
                word=word_upper,
                emoji=emoji,
                confidence=0.9,
                method="gloss-model",
                alternatives=[],
                lottie_file=None,
                semantic_role="OBJECT",
                nearest_neighbors=None,
            ))

        emoji_display = " ".join(c.emoji for c in emoji_cards)
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Done in {processing_time_ms}ms | '{request.text}' → '{gloss_string}'")

        return TranslationResponse(
            original_text=request.text,
            preprocessed_text=preprocessed_text,
            gloss_string=gloss_string,
            emoji_sequence=emoji_cards,
            emoji_display=emoji_display,
            confidence_score=0.9,
            processing_time_ms=processing_time_ms,
            analysis=NLPAnalysis(
                original_text=request.text,
                is_question=False,
                semantic_roles={},
            ),
            raw_ml_prediction=gloss_string,
            warnings=warnings,
            semantic_cluster=None,
            cluster_confidence=None,
            vector_slice=None,
            neighbors=None,
            oov_sequence=[],
        )
