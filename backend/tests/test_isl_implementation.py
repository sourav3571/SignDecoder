import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend and models paths to sys.path
_here = os.path.abspath(__file__)
_backend_dir = os.path.dirname(os.path.dirname(_here))
_models_dir = os.path.join(_backend_dir, "models")
for path in [_backend_dir, _models_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

from app.nlp.isl_config import ISL_CONFIG, ISL_PIPELINE_CONFIG
from app.services.translation_service import TranslationService
from app.models.schemas import TranslationRequest
from emoji_ml.inference import EmojiPredictor

EXAMPLES = [
    {"name": "Simple SOV", "input": "I eat pizza", "expected": "I PIZZA EAT"},
    {"name": "Time-Location Context", "input": "Yesterday I went to school", "expected": "YESTERDAY SCHOOL I GO"},
    {"name": "Question", "input": "Did you go to school today?", "expected": "TODAY SCHOOL YOU GO QUESTION?"},
    {"name": "Negation", "input": "I do not like cold water", "expected": "I WATER COLD LIKE NOT"},
    {"name": "Habitual Time", "input": "Every morning I go to the office", "expected": "MORNING (habitual) OFFICE I GO"},
    {"name": "Spatial Verb", "input": "I gave the book to him", "expected": "I BOOK HIM GIVE (1→3)"},
    {"name": "Classifier Verb", "input": "I drove the car home", "expected": "CAR HOME I DRIVE (CL-3)"},
    {"name": "Emotion", "input": "I am very happy", "expected": "I HAPPY (emphasize^2)"},
]

def run_tests():
    print("=" * 60)
    print("1. VERIFYING COMPONENTS")
    print("=" * 60)
    try:
        predictor = EmojiPredictor()
        print(f"[OK] EmojiPredictor loaded (Vocab size: {len(predictor.vocab)})")
        print(f"[OK] ISL Configuration loaded (Current Sign Language: ISL)")
    except Exception as e:
        print(f"[FAIL] Initialization failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("2. ISL NLP TRANSLATION EXAMPLES")
    print("=" * 60)
    for i, ex in enumerate(EXAMPLES, 1):
        try:
            req = TranslationRequest(text=ex["input"], include_details=True)
            res = TranslationService.translate(req)
            print(f"[{i}] Input   : '{ex['input']}'")
            print(f"    Expected: {ex['expected']}")
            print(f"    Glossed : {res.gloss_string}")
            print(f"    Emojis  : {res.emoji_display} (Confidence: {res.emoji_sequence[0].confidence if res.emoji_sequence else 'N/A'})")
        except Exception as e:
            print(f"[{i}] Error: {e}")

    print("\n" + "=" * 60)
    print("3. ML MODEL INFRASTRUCTURE MAPPING")
    print("=" * 60)
    test_glosses = [
        "YESTERDAY HOME I PIZZA EAT",
        "TODAY SCHOOL YOU GO QUESTION",
        "I WATER COLD LIKE NOT",
        "MOTHER LOVE FAMILY HAPPY"
    ]
    for gloss in test_glosses:
        res = predictor.predict(gloss)
        print(f"  Gloss: {gloss:<30} -> Emojis: {res.get('emoji')}")

    print("\n" + "=" * 60)
    print("ISL PIPELINE CONFIGURATION")
    print("=" * 60)
    print(f"Grammar Rules : {list(ISL_CONFIG['grammar'].keys())}")
    print(f"Features      : {list(ISL_CONFIG['linguistic_features'].keys())}")
    print(f"Pipeline      : {[k for k, v in ISL_PIPELINE_CONFIG.items() if v.get('enabled')]}")

if __name__ == "__main__":
    run_tests()
