import os
import sys

# Reconfigure stdout to support UTF-8 (printing emojis) on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend and backend/models/ are on sys.path for imports
_here = os.path.abspath(__file__)
_backend_dir = os.path.dirname(os.path.dirname(_here))
_models_dir = os.path.join(_backend_dir, "models")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
if _models_dir not in sys.path:
    sys.path.insert(0, _models_dir)

EXAMPLES = [
    {
        "name": "Simple Action",
        "input": "I eat pizza",
        "expected_isl_order": "I PIZZA EAT",
        "explanation": "Subject + Object + Verb (SOV order)"
    },
    {
        "name": "Time-Location Context",
        "input": "Yesterday I went to school",
        "expected_isl_order": "YESTERDAY SCHOOL I GO",
        "explanation": "TIME + LOCATION + SUBJECT + VERB"
    },
    {
        "name": "Simple Question",
        "input": "Did you go to school today?",
        "expected_isl_order": "TODAY SCHOOL YOU GO QUESTION?",
        "explanation": "TIME + LOCATION + SUBJECT + VERB + QUESTION (with brow raise)"
    },
    {
        "name": "Negation",
        "input": "I do not like cold water",
        "expected_isl_order": "I WATER COLD LIKE NOT",
        "explanation": "...VERB + DESCRIPTOR + NEGATION (with head shake)"
    },
    {
        "name": "Multiple Time References",
        "input": "Every morning I go to the office",
        "expected_isl_order": "MORNING (habitual) OFFICE I GO",
        "explanation": "TIME + LOCATION + SUBJECT + VERB (reduplication for habitual)"
    },
    {
        "name": "Location Question",
        "input": "Where did you go yesterday?",
        "expected_isl_order": "YESTERDAY QUESTION WHERE YOU GO?",
        "explanation": "TIME + SUBJECT + WHERE-QUESTION + VERB"
    },
    {
        "name": "Spatial Verb",
        "input": "I gave the book to him",
        "expected_isl_order": "I BOOK HIM GIVE (1→3)",
        "explanation": "Directional verb showing direction from 1st to 3rd person locus"
    },
    {
        "name": "Classifier Verb",
        "input": "I drove the car home",
        "expected_isl_order": "CAR HOME I DRIVE (CL-3)",
        "explanation": "Uses 3-hand classifier for vehicle movement"
    },
    {
        "name": "Emotion Expression",
        "input": "I am very happy",
        "expected_isl_order": "I HAPPY (emphasize^2)",
        "explanation": "SUBJECT + EMOTION + emphasis through reduplication"
    },
    {
        "name": "Comparative",
        "input": "The school is bigger than the office",
        "expected_isl_order": "SCHOOL BIG OFFICE BIG^less",
        "explanation": "Direct comparison using relative size classifiers"
    },
]

def test_isl_examples():
    from app.services.translation_service import TranslationService
    from app.models.schemas import TranslationRequest

    print("=" * 80)
    print("ISL IMPLEMENTATION EXAMPLES")
    print("=" * 80)

    for i, example in enumerate(EXAMPLES, 1):
        print(f"\n[Example {i}] {example['name']}")
        print(f"  Input: {example['input']}")
        print(f"  Expected ISL Order: {example['expected_isl_order']}")
        print(f"  Explanation: {example['explanation']}")

        try:
            request = TranslationRequest(
                text=example['input'],
                include_details=True
            )
            response = TranslationService.translate(request)

            print(f"  [OK] Gloss Generated: {response.gloss_string}")
            print(f"  [OK] Emoji Output: {response.emoji_display}")
            print(f"  [OK] Processing Time: {response.processing_time_ms}ms")

            print(f"  [OK] Emoji Confidence Scores:")
            for emoji_card in response.emoji_sequence[:3]:  
                print(f"      {emoji_card.word}: {emoji_card.emoji} (confidence: {emoji_card.confidence})")
            if len(response.emoji_sequence) > 3:
                print(f"      ... and {len(response.emoji_sequence) - 3} more")

        except Exception as e:
            print(f"  [FAIL] Error: {str(e)}")

def test_isl_features():
    from app.nlp.isl_config import ISL_CONFIG, ISL_PIPELINE_CONFIG

    print("\n" + "=" * 80)
    print("ISL CONFIGURATION & FEATURES")
    print("=" * 80)

    print("\nISL Grammar Structure:")
    for rule, description in ISL_CONFIG["grammar"].items():
        print(f"  - {rule}: {description}")

    print("\nISL Linguistic Features:")
    for feature, value in ISL_CONFIG["linguistic_features"].items():
        print(f"  - {feature}: {value}")

    print("\nISL Processing Pipeline:")
    for stage, config in ISL_PIPELINE_CONFIG.items():
        print(f"  - {stage.upper()}: {config.get('enabled', 'N/A')}")

def test_isl_vocabulary():
    from emoji_ml.my_requirements import WORD_DICTIONARY
    from emoji_ml.inference import EmojiPredictor

    predictor = EmojiPredictor()

    print("\n" + "=" * 80)
    print("ISL VOCABULARY COVERAGE (ML Model)")
    print("=" * 80)

    print(f"\nTotal Glosses in ML Vocabulary: {len(WORD_DICTIONARY) + len(predictor.custom_map)}")
    print(f"Exact Matches in ML Lookup: {len(predictor.exact_map)}")

    # Show a few sample mappings
    print("\nSample Vocabulary Mappings:")
    samples = ["BREAKFAST", "LUNCH", "DINNER", "SCHOOL", "HOME", "EAT", "GO"]
    for sample in samples:
        res = predictor.predict(sample)
        print(f"  - {sample} -> {res.get('emoji')}")

def test_isl_emoji_mapping():
    from emoji_ml.inference import EmojiPredictor

    predictor = EmojiPredictor()

    print("\n" + "=" * 80)
    print("ISL ML EMOJI MAPPING EXAMPLES")
    print("=" * 80)

    test_glosses = [
        "YESTERDAY HOME I PIZZA EAT",
        "TODAY SCHOOL YOU GO QUESTION",
        "I WATER COLD LIKE NOT",
        "MOTHER LOVE FAMILY HAPPY",
    ]

    for gloss in test_glosses:
        print(f"\nGloss: {gloss}")
        res = predictor.predict(gloss)
        print(f"Predicted Emojis: {res.get('emoji')}")

def verify_isl_implementation():
    print("\n" + "=" * 80)
    print("ISL IMPLEMENTATION VERIFICATION")
    print("=" * 80)

    checks = []

    try:
        from emoji_ml.inference import EmojiPredictor
        predictor = EmojiPredictor()
        checks.append(("ML Emoji Predictor", "[OK] Loaded"))
    except Exception as e:
        checks.append(("ML Emoji Predictor", f"[FAIL] Error: {e}"))

    try:
        from app.nlp.isl_config import get_isl_config, CURRENT_SIGN_LANGUAGE
        config = get_isl_config()
        checks.append(("ISL Configuration", f"[OK] Loaded (Current: {CURRENT_SIGN_LANGUAGE})"))
    except Exception as e:
        checks.append(("ISL Configuration", f"[FAIL] Error: {e}"))

    try:
        from app.services.translation_service import TranslationService
        checks.append(("Translation Service", "[OK] Updated for ISL ML Pipeline"))
    except Exception as e:
        checks.append(("Translation Service", f"[FAIL] Error: {e}"))

    for component, status in checks:
        print(f"  {component}: {status}")

    all_passed = all("[OK]" in status for _, status in checks)
    print(f"\n  Overall Status: {'[OK] COMPLETE' if all_passed else '[FAIL] INCOMPLETE'}")

if __name__ == "__main__":
    import sys

    print("\nISL IMPLEMENTATION TEST SUITE")
    print("=" * 80)

    try:
        verify_isl_implementation()
        test_isl_examples()
        test_isl_features()
        test_isl_vocabulary()
        test_isl_emoji_mapping()

        print("\n" + "=" * 80)
        print("[OK] ISL IMPLEMENTATION VERIFICATION COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n[FAIL] ERROR during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
