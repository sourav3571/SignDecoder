import time
import os
import sys
import re
import logging
from app.models.schemas import TranslationRequest, TranslationResponse, EmojiCard, NLPAnalysis
CURRENT_SIGN_LANGUAGE = "ISL"


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
_linker_instance = None

def get_lexical_simplification_dir():
    _here = os.path.abspath(__file__)
    current_dir = os.path.dirname(_here)
    for _ in range(5):
        candidate = os.path.join(current_dir, "model for lexical simplification")
        if os.path.isdir(candidate):
            return candidate
        current_dir = os.path.dirname(current_dir)
    # Fallback to default local dev structure
    _backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(_here)))
    return os.path.join(os.path.dirname(_backend_dir), "model for lexical simplification")

def get_linker():
    global _linker_instance
    if _linker_instance is None:
        import os
        import sys
        lexical_dir = get_lexical_simplification_dir()
        if lexical_dir not in sys.path:
            sys.path.insert(0, lexical_dir)
        try:
            from visual_linker import VisualWordLinker
            _linker_instance = VisualWordLinker()
            logger.info("VisualWordLinker initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize VisualWordLinker: {e}")
    return _linker_instance
def get_simplifier():
    global _simplifier_instance
    if _simplifier_instance is None:
        import os
        import sys
        import torch
        import shutil
        from huggingface_hub import hf_hub_download
        
        # Save original CWD
        original_cwd = os.getcwd()
        
        # Resolve paths
        lexical_dir = get_lexical_simplification_dir()
        
        if lexical_dir not in sys.path:
            sys.path.insert(0, lexical_dir)
            
        os.chdir(lexical_dir)
        
        # Ensure model weights are downloaded if missing (e.g. in Hugging Face Spaces)
        needed_models = [
            "cwi_bert_figurative_v2.pt",
            "idiom_classifier.pt",
            "metaphor_detector.pt",
            "gated_fusion_ranker.pt"
        ]
        for model_file in needed_models:
            local_model_path = os.path.join(lexical_dir, model_file)
            if not os.path.exists(local_model_path):
                logger.info(f"Model file '{model_file}' not found locally. Downloading from Hugging Face Hub...")
                try:
                    downloaded = hf_hub_download(
                        repo_id="souravbehera3571/signdecoder-lexical-models",
                        filename=model_file
                    )
                    shutil.copy(downloaded, local_model_path)
                    logger.info(f"Successfully downloaded and placed '{model_file}'!")
                except Exception as ex:
                    logger.warning(f"Could not download '{model_file}' from Hub: {ex}")
                    
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
        simplification_details = None
        if getattr(request, 'simplify', False):
            try:
                simplifier = get_simplifier()
                preprocessed_text = simplifier.simplify(request.text, verbose=False)
                logger.info(f"Lexically simplified: '{request.text}' → '{preprocessed_text}'")
                if preprocessed_text.lower().strip() != request.text.lower().strip():
                    warnings.append(f"Lexically simplified input from: '{request.text}'")
                simplification_details = getattr(simplifier, 'last_visual_data', None)
            except Exception as e:
                logger.error(f"Lexical simplification failed: {e}")
                warnings.append(f"Simplification error: {str(e)}")

        # ── Step 1: Run the model — input → gloss ──────────────────────────────
        gloss_string = ""
        try:
            from sentence_to_gloss.gloss_model_use import generate_pos_tags, translate_to_isl
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
        linker = get_linker()
        for word in gloss_words:
            word_upper = word.upper()
            word_lower = word.lower()
            
            # Map standard emoji using GLOSS_TO_EMOJI or fallback to VisualWordLinker
            emoji = GLOSS_TO_EMOJI.get(word_upper)
            if not emoji or emoji == "❓":
                if linker:
                    emoji = linker.get_emoji(word_lower)
                else:
                    emoji = "❓"

            # Get visual details from linker for this word
            visual_details = None
            if linker:
                try:
                    details = linker.get_word_details(word_lower)
                    images = linker.image_generator.get_all_links(word_lower)
                    
                    import wordfreq
                    zipf = wordfreq.zipf_frequency(word_lower, 'en')
                    difficulty = max(0.0, min(1.0, (8.0 - zipf) / 8.0)) if zipf > 0 else 0.5
                    
                    visual_details = {
                        "original_word": word_lower,
                        "emoji": emoji,
                        "definition": details.get("definition", "Definition unavailable."),
                        "pronunciation": details.get("pronunciation", f"/{word_lower}/"),
                        "example": details.get("example", f"The {word_lower} was observed."),
                        "images": {
                            "wikimedia": images.get("wikimedia"),
                            "unsplash": images.get("unsplash"),
                            "primary": images.get("primary")
                        },
                        "links": {
                            "merriam_webster": images.get("merriam_webster"),
                            "oxford": images.get("oxford"),
                            "google_images": images.get("google_images"),
                            "wikipedia": images.get("wikipedia")
                        },
                        "complexity_score": {
                            "value": round(difficulty, 2)
                        }
                    }
                except Exception as ex:
                    logger.warning(f"Failed to generate visual details for '{word_lower}': {ex}")

            emoji_cards.append(EmojiCard(
                word=word_upper,
                emoji=emoji,
                confidence=0.9,
                method="gloss-model",
                alternatives=[],
                lottie_file=None,
                semantic_role="OBJECT",
                nearest_neighbors=None,
                visual_details=visual_details
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
            simplification_details=simplification_details,
        )
