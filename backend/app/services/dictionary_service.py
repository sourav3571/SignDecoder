import httpx
import logging
import os
import urllib.parse
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class DictionaryService:
    @staticmethod
    async def get_gloss_details(word: str) -> Dict[str, Any]:
        """
        Fetch rich visual dictionary details for a specific gloss word.
        Uses the Gemini API if GEMINI_API_KEY is configured, with fallback to local heuristics.
        """
        word_clean = word.lower().strip()
        api_key = settings.GEMINI_API_KEY

        # Set up default fallback data
        fallback_data = {
            "word": word.upper(),
            "definition": f"The concept of '{word_clean}'.",
            "sign_handshape": "Varies",
            "sign_location": "General signing space",
            "sign_movement": "Consult sign video/dictionary",
            "sign_explanation": "Follow standard Indian Sign Language (ISL) or American Sign Language (ASL) tutorials for this term.",
            "mnemonic_tip": f"Visualize the concept of {word_clean}.",
            "image_url": f"https://loremflickr.com/800/600/{urllib.parse.quote_plus(word_clean)}",
            "video_url": f"https://www.youtube.com/results?search_query=how+to+sign+{urllib.parse.quote_plus(word_clean)}+in+sign+language",
            "emoji": "❓"
        }

        # Try to use VisualWordLinker for better initial fallbacks if possible
        try:
            from app.services.translation_service import get_linker
            linker = get_linker()
            if linker:
                details = linker.get_word_details(word_clean)
                emoji = linker.get_emoji(word_clean)
                fallback_data["definition"] = details.get("definition", fallback_data["definition"])
                fallback_data["example"] = details.get("example", "")
                fallback_data["emoji"] = emoji if emoji != "❓" else fallback_data["emoji"]
        except Exception as e:
            logger.warning(f"Failed to fetch linker fallbacks: {e}")

        if not api_key or "AIzaSy" not in api_key:
            logger.warning("GEMINI_API_KEY is not configured. Using fallback dictionary lookup.")
            return fallback_data

        prompt = f"""
        You are an expert Sign Language Instructor and Lexical Dictionary designer.
        Provide a deep-dive visual dictionary entry for the English word: "{word_clean}".
        It should include exact descriptions of how to perform its sign language representation (handshape, location, movement, explanation), a helpful mnemonic memory tip, and a clean, high-quality, descriptive search query for a real-world photograph representing the word.
        
        Respond ONLY with a JSON object containing these exact fields:
        {{
          "definition": "A clear, concise, and easy-to-understand dictionary definition of the word.",
          "sign_handshape": "Brief description of the handshape(s) used (e.g., 'Flat B-hand', 'Pointed Index finger', 'Clenched fist').",
          "sign_location": "Where in space or on the body the sign is made (e.g., 'In front of chest', 'At the temple', 'Near the chin').",
          "sign_movement": "The direction, speed, and path of the hands (e.g., 'Moved downward in a wavy line', 'Tapped twice on the chest').",
          "sign_explanation": "A complete step-by-step description of how to make the sign from start to finish.",
          "mnemonic_tip": "A fun or visual memory trick to help someone remember this sign.",
          "image_search_query": "A search query for a real-world, high-quality photograph representing this concept (e.g. 'fresh red apple on table' for apple, 'dog running in grass' for dog). Do not include words like 'illustration' or 'vector'.",
          "emoji": "The single most appropriate emoji that represents this word."
        }}
        """

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "thinkingConfig": {
                    "thinkingBudget": 0
                }
            }
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    resp_json = response.json()
                    text_content = resp_json["contents"][0]["parts"][0]["text"]
                    
                    import json
                    parsed = json.loads(text_content.strip())
                    
                    # Construct rich response
                    search_query = parsed.get("image_search_query", word_clean)
                    image_url = f"https://loremflickr.com/800/600/{urllib.parse.quote_plus(search_query)}"
                    video_url = f"https://www.youtube.com/results?search_query=how+to+sign+{urllib.parse.quote_plus(word_clean)}+in+sign+language"
                    
                    return {
                        "word": word.upper(),
                        "definition": parsed.get("definition", fallback_data["definition"]),
                        "sign_handshape": parsed.get("sign_handshape", fallback_data["sign_handshape"]),
                        "sign_location": parsed.get("sign_location", fallback_data["sign_location"]),
                        "sign_movement": parsed.get("sign_movement", fallback_data["sign_movement"]),
                        "sign_explanation": parsed.get("sign_explanation", fallback_data["sign_explanation"]),
                        "mnemonic_tip": parsed.get("mnemonic_tip", fallback_data["mnemonic_tip"]),
                        "image_url": image_url,
                        "video_url": video_url,
                        "emoji": parsed.get("emoji", fallback_data["emoji"])
                    }
                else:
                    logger.error(f"Gemini API returned error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Error querying Gemini API: {e}")

        return fallback_data
