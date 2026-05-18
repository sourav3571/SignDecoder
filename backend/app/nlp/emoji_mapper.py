from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EmojiMapper:

    def __init__(self, sbert_model_name: str = "all-MiniLM-L6-v2"):
        self.sbert_model_name = sbert_model_name
        self.model = None
        self._load_model()

        self.dictionary = {
            "EAT": {"emoji": "🍽️", "lottie": "eat.json", "alternatives": ["🍕", "🍔"]},
            "BREAKFAST": {"emoji": "🥣", "lottie": "breakfast.json", "alternatives": ["🥞", "🍳"]},
            "HOME": {"emoji": "🏠", "lottie": "home.json", "alternatives": ["🏘️"]},
            "YESTERDAY": {"emoji": "⏪", "lottie": "yesterday.json", "alternatives": ["📅"]},
            "I": {"emoji": "🙋", "lottie": "me.json", "alternatives": ["👤"]},
            "YOU": {"emoji": "👉", "lottie": "you.json", "alternatives": ["👤"]},
            "HE": {"emoji": "👨", "lottie": "he.json", "alternatives": ["👦"]},
            "SHE": {"emoji": "👩", "lottie": "she.json", "alternatives": ["👧"]},
            "WE": {"emoji": "👥", "lottie": "we.json", "alternatives": ["👫"]},
            "THEY": {"emoji": "🗣️", "lottie": "they.json", "alternatives": ["👨‍👩‍👧‍👦"]},
            "CAR": {"emoji": "🚗", "lottie": "car.json", "alternatives": ["🚙"]},
            "GO": {"emoji": "🚶", "lottie": "go.json", "alternatives": ["➡️"]},
            "WANT": {"emoji": "🤲", "lottie": "want.json", "alternatives": ["🙏"]},
            "LIKE": {"emoji": "👍", "lottie": "like.json", "alternatives": ["❤️"]},
            "LOVE": {"emoji": "❤️", "lottie": "love.json", "alternatives": ["😍"]},
            "WATER": {"emoji": "💧", "lottie": "water.json", "alternatives": ["🌊", "🚰"]},
            "FOOD": {"emoji": "🍱", "lottie": "food.json", "alternatives": ["🍎"]},
            "HELLO": {"emoji": "👋", "lottie": "hello.json", "alternatives": ["🤝"]},
            "PLEASE": {"emoji": "🥺", "lottie": "please.json", "alternatives": ["🙏"]},
            "HAPPY": {"emoji": "😊", "lottie": "happy.json", "alternatives": ["😁"]},
            "SAD": {"emoji": "😢", "lottie": "sad.json", "alternatives": ["😞"]},
            "SCHOOL": {"emoji": "🏫", "lottie": "school.json", "alternatives": ["🎒"]},
            "WORK": {"emoji": "💼", "lottie": "work.json", "alternatives": ["🏢"]},
            "SLEEP": {"emoji": "😴", "lottie": "sleep.json", "alternatives": ["🛌"]},
            "TODAY": {"emoji": "📅", "lottie": "today.json", "alternatives": ["☀️"]},
            "TOMORROW": {"emoji": "⏩", "lottie": "tomorrow.json", "alternatives": ["🌅"]},
            "NOT": {"emoji": "❌", "lottie": "not.json", "alternatives": ["🚫"]},
            "?": {"emoji": "❓", "lottie": "question.json", "alternatives": ["🤔"]}
        }

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer

            logger.info("SBERT loading bypassed for local dev.")
        except ImportError:
            logger.warning("sentence-transformers not installed. Vector matching disabled.")

    def map_gloss(self, gloss_sequence: List[str]) -> List[Dict[str, Any]]:

        results = []
        for word in gloss_sequence:
            word_upper = word.upper()

            if word_upper in self.dictionary:
                entry = self.dictionary[word_upper]
                results.append({
                    "word": word_upper,
                    "emoji": entry["emoji"],
                    "confidence": 1.0,
                    "method": "exact",
                    "alternatives": entry.get("alternatives", []),
                    "lottie_file": entry.get("lottie")
                })
                continue

            fallback_emoji = "👤" if word_upper.istitle() else "❔"
            results.append({
                "word": word_upper,
                "emoji": fallback_emoji,
                "confidence": 0.3,
                "method": "fallback",
                "alternatives": [],
                "lottie_file": None
            })

        return results

emoji_mapper = EmojiMapper()
