import os
import json

# Fallback emoji-to-word dictionary containing some standard mappings
EMOJI_TO_WORD = {
    "❤️": "love",
    "🍕": "pizza",
    "👋": "hello",
    "😊": "happy",
    "🙏": "please",
    "🥺": "pleading",
    "😔": "sad",
    "✅": "yes",
    "❌": "no",
    "🤔": "thinking",
    "👍": "like",
    "👎": "dislike",
    "🌧️": "rain",
    "☀️": "sun",
    "🌊": "ocean",
    "🍔": "burger",
    "🚗": "car",
    "🏫": "school",
    "💻": "computer",
    "📱": "phone",
    "📚": "books",
    "🏥": "hospital",
    "💊": "pill",
}

# Fallback word-to-emoji mapping
WORD_TO_EMOJI = {
    "love": "❤️",
    "pizza": "🍕",
    "hello": "👋",
    "happy": "😊",
    "please": "🙏",
    "pleading": "🥺",
    "sad": "😔",
    "yes": "✅",
    "no": "❌",
    "thinking": "🤔",
    "like": "👍",
    "dislike": "👎",
    "rain": "🌧️",
    "sun": "☀️",
    "ocean": "🌊",
    "burger": "🍔",
    "car": "🚗",
    "school": "🏫",
    "computer": "💻",
    "phone": "📱",
    "books": "📚",
    "hospital": "🏥",
    "pill": "💊",
}

# Dynamically load and reverse label_to_emoji.json if available
try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
    potential_paths = [
        os.path.join(_HERE, "..", "..", "backend", "models", "emoji_ml", "label_to_emoji.json"),
        os.path.join(_HERE, "label_to_emoji.json"),
        r"d:\SignDecoder\backend\models\emoji_ml\label_to_emoji.json"
    ]
    for path in potential_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                label_to_emoji = json.load(f)
                for label, emoji in label_to_emoji.items():
                    # Map both the raw label and lowercase forms
                    WORD_TO_EMOJI[label] = emoji
                    WORD_TO_EMOJI[label.lower()] = emoji
                    WORD_TO_EMOJI[label.replace("_", " ").lower()] = emoji
                    
                    # Reverse map
                    clean_label = label.replace("_", " ")
                    EMOJI_TO_WORD[emoji] = clean_label
            break
except Exception:
    pass

def map_emojis_to_words(emoji_sequence_str: str) -> list[str]:
    """
    Split the space-separated emoji sequence, lookup each emoji in the EMOJI_TO_WORD mapping,
    and return the list of mapped text tokens.
    """
    emojis = emoji_sequence_str.strip().split()
    mapped_tokens = []
    for em in emojis:
        # Get mapping or fallback to 'unknown'
        token = EMOJI_TO_WORD.get(em, EMOJI_TO_WORD.get(em.strip(), "unknown"))
        mapped_tokens.append(token)
    return mapped_tokens

def map_words_to_emojis(word_sequence_str: str) -> str:
    """
    Translates a sequence of labels/words (e.g., "[rain] [day]" or "rain day")
    into a sequence of emojis (e.g., "🌧️ ☀️") using the local dictionary.
    """
    tokens = word_sequence_str.strip().split()
    emojis = []
    for token in tokens:
        # Clean the token: strip brackets and punctuation
        clean_token = token.strip("[].,!?;:\"'").lower()
        if clean_token in WORD_TO_EMOJI:
            emojis.append(WORD_TO_EMOJI[clean_token])
        else:
            token_raw = token.strip("[]")
            if token_raw in WORD_TO_EMOJI:
                emojis.append(WORD_TO_EMOJI[token_raw])
            else:
                emojis.append(token)  # Keep the token as-is if no mapping exists
    return " ".join(emojis)
