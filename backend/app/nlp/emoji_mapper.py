from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EmojiMapper:
    """
    Maps Sign Language Gloss words to Emojis and Lottie Animation files.
    Uses Exact Matching, Vector Similarity (SBERT), and Fallbacks.
    """
    def __init__(self, sbert_model_name: str = "all-MiniLM-L6-v2"):
        self.sbert_model_name = sbert_model_name
        self.model = None
        self._load_model()
        
        # Hardcoded dictionary for MVP. In production, this comes from MongoDB.
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
            # Uncomment to load the model locally
            # self.model = SentenceTransformer(self.sbert_model_name)
            # logger.info(f"Loaded SBERT model: {self.sbert_model_name}")
            logger.info("SBERT loading bypassed for local dev.")
        except ImportError:
            logger.warning("sentence-transformers not installed. Vector matching disabled.")
            
    def map_gloss(self, gloss_sequence: List[str]) -> List[Dict[str, Any]]:
        """
        Takes a list of gloss words and maps them to visual representations.
        """
        results = []
        for word in gloss_sequence:
            word_upper = word.upper()
            
            # Strategy 1: Exact Match
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
                
            # Strategy 2: SBERT Semantic Search (Mocked for now)
            # In production, query Pinecone here.
            
            # Strategy 5: Fallback
            # Determine if it looks like a person's name or unknown concept
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

# Singleton instance
emoji_mapper = EmojiMapper()
