import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Set path to include backend models
backend_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(backend_dir, "models")
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from emoji_ml.inference import EmojiPredictor

TEST_CASES = [
    # 10 Out-of-vocabulary words/synonyms
    "furious",
    "delighted",
    "miserable",
    "chilly",
    "blazing",
    "automobile",
    "physician",
    "dine",
    "residence",
    "ocean",
    
    # 10 Out-of-vocabulary sentences
    "I feel extremely exhausted today",
    "The weather is very sunny",
    "Where is the hospital",
    "She is crying because she is sad",
    "Let us go eat breakfast",
    "A fast red vehicle",
    "My school starts early",
    "They are laughing at the joke",
    "It is raining heavily outside",
    "He is smiling with joy"
]

def run_generalization_tests():
    print("Initializing EmojiPredictor semantic model...")
    predictor = EmojiPredictor()
    print("Model initialized successfully.\n")
    
    print("=" * 90)
    print(f"{'INPUT TEXT':<35} | {'PREDICTED EMOJI':<18} | {'SEMANTIC CLUSTER':<18} | {'CONFIDENCE'}")
    print("=" * 90)
    
    for text in TEST_CASES:
        res = predictor.predict(text)
        emoji_str = res.get("emoji", "")
        cluster = res.get("semantic_cluster", "NEUTRAL")
        conf = res.get("cluster_confidence", 0.0)
        
        # Clean print format
        print(f"{text:<35} | {emoji_str:<18} | {cluster:<18} | {conf * 100:.1f}%")
        
    print("=" * 90)

if __name__ == "__main__":
    run_generalization_tests()
