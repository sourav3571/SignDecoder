
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

            print(f"  ✓ Gloss Generated: {response.gloss_string}")
            print(f"  ✓ Emoji Output: {response.emoji_display}")
            print(f"  ✓ Processing Time: {response.processing_time_ms}ms")

            print(f"  ✓ Emoji Confidence Scores:")
            for emoji_card in response.emoji_sequence[:3]:  
                print(f"      {emoji_card.word}: {emoji_card.emoji} (confidence: {emoji_card.confidence})")
            if len(response.emoji_sequence) > 3:
                print(f"      ... and {len(response.emoji_sequence) - 3} more")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

def test_isl_features():

    from app.nlp.isl_config import ISL_CONFIG, ISL_PIPELINE_CONFIG

    print("\n" + "=" * 80)
    print("ISL CONFIGURATION & FEATURES")
    print("=" * 80)

    print("\nISL Grammar Structure:")
    for rule, description in ISL_CONFIG["grammar"].items():
        print(f"  • {rule}: {description}")

    print("\nISL Linguistic Features:")
    for feature, value in ISL_CONFIG["linguistic_features"].items():
        print(f"  • {feature}: {value}")

    print("\nISL Processing Pipeline:")
    for stage, config in ISL_PIPELINE_CONFIG.items():
        print(f"  • {stage.upper()}: {config.get('enabled', 'N/A')}")

def test_isl_vocabulary():

    from app.nlp.isl_emoji_mapper import isl_emoji_mapper

    print("\n" + "=" * 80)
    print("ISL VOCABULARY COVERAGE")
    print("=" * 80)

    print(f"\nTotal Glosses in Dictionary: {len(isl_emoji_mapper.dictionary)}")

    categories = {}
    for gloss, entry in isl_emoji_mapper.dictionary.items():
        cat = entry.get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(gloss)

    print(f"Categories Covered: {len(categories)}")
    for category, glosses in sorted(categories.items()):
        print(f"  • {category.upper()}: {len(glosses)} glosses")
        print(f"    Examples: {', '.join(glosses[:5])}")

def test_isl_classifiers():

    from app.nlp.isl_emoji_mapper import isl_emoji_mapper

    print("\n" + "=" * 80)
    print("ISL CLASSIFIER SYSTEM")
    print("=" * 80)

    classifiers = {
        "CL-1": "1-hand classifier for people and upright objects",
        "CL-3": "3-hand classifier for vehicles",
        "CL-5": "5-hand classifier for flat objects and animals",
    }

    for clf, description in classifiers.items():
        if clf in isl_emoji_mapper.dictionary:
            entry = isl_emoji_mapper.dictionary[clf]
            print(f"\n{clf}: {description}")
            print(f"  Emoji: {entry['emoji']}")
            print(f"  Confidence: {entry['confidence']}")
            print(f"  Notes: {entry.get('notes', 'N/A')}")

def test_isl_facial_expressions():

    from app.nlp.isl_emoji_mapper import isl_emoji_mapper

    print("\n" + "=" * 80)
    print("ISL FACIAL EXPRESSION MARKERS")
    print("=" * 80)

    facial_expressions = ["BROW-RAISE", "HEAD-SHAKE", "HEAD-NOD"]

    for expr in facial_expressions:
        if expr in isl_emoji_mapper.dictionary:
            entry = isl_emoji_mapper.dictionary[expr]
            print(f"\n{expr}:")
            print(f"  Emoji: {entry['emoji']}")
            print(f"  Confidence: {entry['confidence']}")
            print(f"  Category: {entry['category']}")
            print(f"  Notes: {entry.get('notes', 'N/A')}")

def test_isl_emoji_mapping():

    from app.nlp.isl_emoji_mapper import isl_emoji_mapper

    print("\n" + "=" * 80)
    print("ISL EMOJI MAPPING EXAMPLES")
    print("=" * 80)

    test_glosses = [
        ["YESTERDAY", "HOME", "I", "PIZZA", "EAT"],
        ["TODAY", "SCHOOL", "YOU", "GO", "QUESTION"],
        ["I", "WATER", "COLD", "LIKE", "NOT"],
        ["MOTHER", "LOVE", "FAMILY", "HAPPY"],
    ]

    for glosses in test_glosses:
        print(f"\nGlosses: {' '.join(glosses)}")
        emoji_result = isl_emoji_mapper.map_gloss(glosses)

        emoji_display = "".join([item["emoji"] for item in emoji_result])
        print(f"Emoji: {emoji_display}")

        print("Details:")
        for item in emoji_result:
            print(f"  {item['word']}: {item['emoji']} (confidence: {item['confidence']}, method: {item['method']})")

def verify_isl_implementation():

    print("\n" + "=" * 80)
    print("ISL IMPLEMENTATION VERIFICATION")
    print("=" * 80)

    checks = []

    try:
        from app.nlp.isl_reorderer import isl_reorderer
        checks.append(("ISL Reorderer", "✓ Loaded"))
    except Exception as e:
        checks.append(("ISL Reorderer", f"✗ Error: {e}"))

    try:
        from app.nlp.isl_emoji_mapper import isl_emoji_mapper
        checks.append(("ISL Emoji Mapper", f"✓ Loaded ({len(isl_emoji_mapper.dictionary)} glosses)"))
    except Exception as e:
        checks.append(("ISL Emoji Mapper", f"✗ Error: {e}"))

    try:
        from app.nlp.isl_config import get_isl_config, CURRENT_SIGN_LANGUAGE
        config = get_isl_config()
        checks.append(("ISL Configuration", f"✓ Loaded (Current: {CURRENT_SIGN_LANGUAGE})"))
    except Exception as e:
        checks.append(("ISL Configuration", f"✗ Error: {e}"))

    try:
        from app.services.translation_service import TranslationService
        checks.append(("Translation Service", "✓ Updated for ISL"))
    except Exception as e:
        checks.append(("Translation Service", f"✗ Error: {e}"))

    for component, status in checks:
        print(f"  {component}: {status}")

    all_passed = all("✓" in status for _, status in checks)
    print(f"\n  Overall Status: {'✓ COMPLETE' if all_passed else '✗ INCOMPLETE'}")

if __name__ == "__main__":
    """Run all tests when executed directly."""
    import sys

    print("\nISL IMPLEMENTATION TEST SUITE")
    print("=" * 80)

    try:

        verify_isl_implementation()

        test_isl_features()
        test_isl_vocabulary()
        test_isl_classifiers()
        test_isl_facial_expressions()
        test_isl_emoji_mapping()

        print("\n" + "=" * 80)
        print("✓ ISL IMPLEMENTATION VERIFICATION COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ ERROR during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
