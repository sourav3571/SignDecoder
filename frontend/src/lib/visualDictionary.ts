const visualCache = new Map<string, { imageUrl: string; extract: string }>();

const SIGN_CONTEXT_MAP: Record<string, string> = {
  cake: "birthday cake dessert",
  exam: "exam paper student",
  weather: "weather forecast sky",
  doctor: "doctor physician hospital",
  school: "school building classroom",
  water: "water splash drink",
  happy: "happy smiling person",
  sad: "sad crying person",
  arm: "human arm muscle",
  leg: "human leg",
  vehicle: "car vehicle traffic",
  cloud: "cloudy sky nature",
  fire: "burning fire flames",
  house: "house home building",
  book: "open book reading"
};

const EMOJI_FALLBACK: Record<string, string> = {
  exam: "📝",
  cake: "🎂",
  weather: "🌤️",
  cloud: "☁️",
  vehicle: "🚗",
  arm: "💪",
  leg: "🦵",
  school: "🏫",
  doctor: "👨‍⚕️",
  book: "📚",
  house: "🏠",
  water: "💧",
  fire: "🔥",
  happy: "😊",
  sad: "😢"
};

const getEmojiSvgUrl = (emoji: string) => {
  return `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">${emoji}</text></svg>`;
};

export async function getConceptVisuals(word: string): Promise<{ imageUrl: string; extract: string }> {
  const normalizedWord = word.toLowerCase().trim();

  if (visualCache.has(normalizedWord)) {
    return visualCache.get(normalizedWord)!;
  }

  const pexelsKey = process.env.NEXT_PUBLIC_PEXELS_KEY;
  let result = { imageUrl: "", extract: "" };

  try {
    // 1. Try Wikipedia REST API
    const wikiRes = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(normalizedWord)}`);
    if (wikiRes.ok) {
      const wikiData = await wikiRes.json();
      if (wikiData.type !== "disambiguation") {
        if (wikiData.thumbnail?.source) {
          result.imageUrl = wikiData.thumbnail.source;
        } else if (wikiData.originalimage?.source) {
          result.imageUrl = wikiData.originalimage.source;
        }
        
        if (wikiData.extract) {
          result.extract = wikiData.extract.length > 100 ? wikiData.extract.substring(0, 100) + '...' : wikiData.extract;
        }
      }
    }

    // 2. Try Pexels API if Wikipedia didn't yield an image
    if (!result.imageUrl && pexelsKey) {
      const searchQuery = SIGN_CONTEXT_MAP[normalizedWord] || normalizedWord;
      const pexelsRes = await fetch(`https://api.pexels.com/v1/search?query=${encodeURIComponent(searchQuery)}&per_page=1`, {
        headers: {
          Authorization: pexelsKey
        }
      });
      if (pexelsRes.ok) {
        const pexelsData = await pexelsRes.json();
        if (pexelsData.photos && pexelsData.photos.length > 0) {
          result.imageUrl = pexelsData.photos[0].src.medium || pexelsData.photos[0].src.original;
        }
      }
    }

    // 3. Fallback to emoji SVG
    if (!result.imageUrl) {
      const fallbackEmoji = EMOJI_FALLBACK[normalizedWord] || "❓";
      result.imageUrl = getEmojiSvgUrl(fallbackEmoji);
    }

  } catch (error) {
    console.error("Error fetching concept visuals:", error);
    // Silent fallback
    const fallbackEmoji = EMOJI_FALLBACK[normalizedWord] || "❓";
    result.imageUrl = getEmojiSvgUrl(fallbackEmoji);
  }

  visualCache.set(normalizedWord, result);
  return result;
}
