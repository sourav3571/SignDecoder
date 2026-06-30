import httpx
import logging
import os
import urllib.parse
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

async def get_wikimedia_image(query: str) -> str:
    """
    Search Wikimedia Commons for a relevant image and return its direct URL.
    Falls back to a loremflickr URL if no image is found or if request fails.
    """
    search_url = "https://commons.wikimedia.org/w/api.php"
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,  # File namespace
        "srlimit": 1,
        "origin": "*"
    }
    headers = {
        "User-Agent": "SignDecoderApp/1.0 (contact: souravbehera3571@gmail.com)"
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(search_url, params=search_params, headers=headers)
            if r.status_code == 200:
                search_data = r.json()
                search_results = search_data.get("query", {}).get("search", [])
                if search_results:
                    file_title = search_results[0].get("title")
                    
                    info_params = {
                        "action": "query",
                        "format": "json",
                        "prop": "imageinfo",
                        "titles": file_title,
                        "iiprop": "url",
                        "origin": "*"
                    }
                    r_info = await client.get(search_url, params=info_params, headers=headers)
                    if r_info.status_code == 200:
                        info_data = r_info.json()
                        pages = info_data.get("query", {}).get("pages", {})
                        for page_id in pages:
                            imageinfo = pages[page_id].get("imageinfo")
                            if imageinfo:
                                return imageinfo[0].get("url")
    except Exception as e:
        logger.warning(f"Error fetching wikimedia image for query '{query}': {e}")
    
    # Fallback to loremflickr if wikimedia fails
    return f"https://loremflickr.com/800/600/{urllib.parse.quote_plus(query)}"

class DictionaryService:
    @staticmethod
    async def get_gloss_details(word: str) -> Dict[str, Any]:
        """
        Fetch simple visual dictionary details for a specific gloss word.
        Uses the Gemini API if GEMINI_API_KEY is configured, with fallback to local heuristics.
        """
        word_clean = word.lower().strip()
        api_key = settings.GEMINI_API_KEY

        # Set up default fallback data
        fallback_image = await get_wikimedia_image(word_clean)
        fallback_data = {
            "word": word.upper(),
            "explanation": f"The concept of '{word_clean}'. To sign this, use natural, expressive gestures in front of the body to convey the meaning clearly.",
            "image_url": fallback_image,
            "emoji": "❓"
        }

        # Try to use VisualWordLinker for better initial fallbacks if possible
        try:
            from app.services.translation_service import get_linker
            linker = get_linker()
            if linker:
                details = linker.get_word_details(word_clean)
                emoji = linker.get_emoji(word_clean)
                fallback_data["explanation"] = details.get("definition", fallback_data["explanation"])
                fallback_data["emoji"] = emoji if emoji != "❓" else fallback_data["emoji"]
        except Exception as e:
            logger.warning(f"Failed to fetch linker fallbacks: {e}")

        if not api_key or "AIzaSy" not in api_key:
            logger.warning("GEMINI_API_KEY is not configured. Using fallback dictionary lookup.")
            return fallback_data

        prompt = f"""
        You are an expert Sign Language Instructor.
        Provide a simple, clear, and easy-to-understand one-paragraph explanation of the concept and how to sign the English word: "{word_clean}".
        Keep it simple, friendly, and accessible to beginners.
        
        Respond ONLY with a JSON object containing these exact fields:
        {{
          "explanation": "A simple 2-3 sentence paragraph explaining both the concept of the word and a simple guide on how to perform its sign language gesture.",
          "image_search_query": "A search query for a real-world, high-quality photograph representing this concept (e.g. 'fresh red apple on table' for apple). Do not include words like 'illustration' or 'vector'.",
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
                    text_content = resp_json["candidates"][0]["content"]["parts"][0]["text"]
                    
                    import json
                    parsed = json.loads(text_content.strip())
                    
                    # Construct rich response
                    search_query = parsed.get("image_search_query", word_clean)
                    image_url = await get_wikimedia_image(search_query)
                    
                    return {
                        "word": word.upper(),
                        "explanation": parsed.get("explanation", fallback_data["explanation"]),
                        "image_url": image_url,
                        "emoji": parsed.get("emoji", fallback_data["emoji"])
                    }
                else:
                    logger.error(f"Gemini API returned error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Error querying Gemini API: {e}")

        return fallback_data
