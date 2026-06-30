const visualCache = new Map<string, { imageUrl: string; extract: string }>();

const STOPWORDS = new Set([
  "the", "a", "an", "is", "was", "were", "be", "been", "being", "have", "has", "had", 
  "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", 
  "shall", "can", "of", "in", "on", "at", "to", "for", "with", "by", "from", "as", 
  "and", "or", "but", "if", "then", "so", "very", "really", "just", "too"
]);

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
  exam: "📝", cake: "🎂", weather: "🌤️", cloud: "☁️", vehicle: "🚗", 
  arm: "💪", leg: "🦵", school: "🏫", doctor: "👨‍⚕️", book: "📚", 
  house: "🏠", water: "💧", fire: "🔥", happy: "😊", sad: "😢",
  easy: "😌", hard: "😣", good: "👍", bad: "👎", big: "🦣", small: "🐁", 
  hot: "🔥", cold: "🥶", eat: "🍽️", drink: "🥤", sleep: "😴", run: "🏃", 
  walk: "🚶", sit: "🪑", stand: "🧍", man: "👨", woman: "👩", child: "🧒", 
  friend: "🤝", family: "👨‍👩‍👧", love: "❤️", work: "💼", play: "🎮", 
  learn: "📖", teach: "👨‍🏫", help: "🙏", money: "💰", time: "⏰", 
  day: "☀️", night: "🌙", year: "📅", today: "📆", tomorrow: "➡️📅", 
  yesterday: "⬅️📅", yes: "✅", no: "❌", please: "🙏", sorry: "😔", 
  thanks: "🙏", hello: "👋", bye: "👋"
};

const getEmojiSvgUrl = (emoji: string) => {
  return `data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">${emoji}</text></svg>`;
};

// Clean gloss modifiers: remove ++, --, _, numbers, and trim
const cleanGlossWord = (word: string) => {
  return word.replace(/[+\-_0-9]/g, "").toLowerCase().trim();
};

export async function getConceptVisuals(word: string): Promise<{ imageUrl: string; extract: string }> {
  const normalizedWord = cleanGlossWord(word);
  console.log("[VisualDict] Searching for:", normalizedWord);

  if (visualCache.has(normalizedWord)) {
    return visualCache.get(normalizedWord)!;
  }

  let result = { imageUrl: "", extract: "" };
  const pexelsKey = process.env.NEXT_PUBLIC_PEXELS_KEY;
  console.log("[VisualDict] Pexels key loaded:", !!pexelsKey);

  // 1. Skip Non-Visual Stopwords directly to Emoji Fallback
  if (STOPWORDS.has(normalizedWord)) {
    console.log("[VisualDict] Skipping stopword:", normalizedWord);
    const fallbackEmoji = EMOJI_FALLBACK[normalizedWord] || "❓";
    result.imageUrl = getEmojiSvgUrl(fallbackEmoji);
    visualCache.set(normalizedWord, result);
    return result;
  }

  try {
    // 2. Try Wikipedia REST API (Lowercase first, then Capitalized)
    const tryWikipedia = async (query: string) => {
      const wikiRes = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(query)}`);
      if (!wikiRes.ok) return false;
      const wikiData = await wikiRes.json();
      if (wikiData.type === "disambiguation") return false;

      if (wikiData.thumbnail?.source) {
        result.imageUrl = wikiData.thumbnail.source;
      } else if (wikiData.originalimage?.source) {
        result.imageUrl = wikiData.originalimage.source;
      }
      if (wikiData.extract) {
        result.extract = wikiData.extract.length > 100 ? wikiData.extract.substring(0, 100) + '...' : wikiData.extract;
      }
      return !!result.imageUrl;
    };

    let wikiSuccess = await tryWikipedia(normalizedWord);
    if (!wikiSuccess) {
      const capitalized = normalizedWord.charAt(0).toUpperCase() + normalizedWord.slice(1);
      wikiSuccess = await tryWikipedia(capitalized);
    }
    console.log("[VisualDict] Wikipedia result:", wikiSuccess ? "success" : "fail");

    // 3. Try Pexels API (Original query, then fallback to " concept")
    if (!result.imageUrl && pexelsKey) {
      const fetchPexels = async (searchQuery: string) => {
        const pexelsRes = await fetch(`https://api.pexels.com/v1/search?query=${encodeURIComponent(searchQuery)}&per_page=1`, {
          headers: { Authorization: pexelsKey }
        });
        if (!pexelsRes.ok) return false;
        const pexelsData = await pexelsRes.json();
        if (pexelsData.photos && pexelsData.photos.length > 0) {
          result.imageUrl = pexelsData.photos[0].src.medium || pexelsData.photos[0].src.original;
          return true;
        }
        return false;
      };

      const primaryQuery = SIGN_CONTEXT_MAP[normalizedWord] || normalizedWord;
      let pexelsSuccess = await fetchPexels(primaryQuery);
      
      if (!pexelsSuccess) {
        pexelsSuccess = await fetchPexels(`${normalizedWord} concept`);
      }
      console.log("[VisualDict] Pexels result:", pexelsSuccess ? "success" : "fail");
    }

    // 4. Fallback to emoji SVG
    if (!result.imageUrl) {
      const fallbackEmoji = EMOJI_FALLBACK[normalizedWord] || "❓";
      result.imageUrl = getEmojiSvgUrl(fallbackEmoji);
    }

  } catch (error) {
    console.error("Error fetching concept visuals:", error);
    const fallbackEmoji = EMOJI_FALLBACK[normalizedWord] || "❓";
    result.imageUrl = getEmojiSvgUrl(fallbackEmoji);
  }

  visualCache.set(normalizedWord, result);
  return result;
}
