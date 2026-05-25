"""
Semantic Analyzer — powered by google/flan-t5-base (seq2seq).

Flan-T5 is prompted with structured instructions to extract:
  subject, verb, object, time, location, modifier, negation
from plain English.  The output is parsed back into the same
dict schema the rest of the pipeline (reorderer, gloss generator)
already expects, so no other files need to change.
"""

from typing import Dict, List, Any, Optional
import logging
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Flan-T5 loader (lazy, singleton)
# ---------------------------------------------------------------------------

_pipeline = None  # HuggingFace text2text-generation pipeline

def _get_pipeline():
    """Load Flan-T5 once and cache it."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    try:
        from transformers import pipeline as hf_pipeline
        logger.info("Loading google/flan-t5-base …")
        _pipeline = hf_pipeline(
            "text2text-generation",
            model="google/flan-t5-base",
            max_new_tokens=256,
        )
        logger.info("✓ Flan-T5 loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load Flan-T5: {e}")
        _pipeline = None

    return _pipeline


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """Extract semantic roles from the English sentence below and return a JSON object with these keys:
subject, verb, object, indirect_object, time, location, modifier, negation, auxiliary, is_question, has_negation.

Rules:
- Each value is a list of words (strings), except is_question and has_negation which are booleans.
- Use base/lemma form for verbs (e.g. "go" not "going").
- Only include words that appear (or are clearly implied) in the sentence.
- If a role is absent, use an empty list [].
- Return valid JSON only — no explanation.

Sentence: {sentence}

JSON:"""


# ---------------------------------------------------------------------------
# Parser for model output
# ---------------------------------------------------------------------------

_ROLE_KEYS = [
    "subject", "verb", "object", "indirect_object",
    "time", "location", "modifier", "negation", "auxiliary",
]

def _parse_flan_output(raw: str) -> Dict[str, Any]:
    """
    Attempt to parse the JSON emitted by Flan-T5.
    Falls back gracefully to empty roles on bad output.
    """
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()

    data = {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                logger.warning("Flan-T5 output could not be parsed as JSON; using heuristic fallback.")

    roles: Dict[str, List[str]] = {}
    for key in _ROLE_KEYS:
        val = data.get(key, [])
        if isinstance(val, list):
            roles[key] = [str(v) for v in val]
        elif isinstance(val, str) and val:
            roles[key] = [val]
        else:
            roles[key] = []

    is_question = bool(data.get("is_question", False))
    has_negation = bool(data.get("has_negation", bool(roles["negation"])))

    return roles, is_question, has_negation


_FALLBACK_NEGATION_WORDS = {"not", "no", "never", "n't"}
_FALLBACK_TIME_WORDS = {
    "yesterday", "today", "tomorrow", "morning", "afternoon",
    "evening", "night", "now", "later", "soon", "ago",
}
_FALLBACK_LOCATION_WORDS = {
    "home", "work", "office", "park", "school", "store", "hospital",
    "market", "temple", "road", "here", "there", "sofa", "restaurant",
}
_FALLBACK_SUBJECT_PRONOUNS = {"i", "you", "he", "she", "we", "they", "it"}
_FALLBACK_OBJECT_PRONOUNS = {"me", "him", "her", "us", "them"}
_FALLBACK_QUESTION_WORDS = {"what", "where", "when", "why", "how", "who", "which", "whom"}
_FALLBACK_ACTION_WORDS = {
    "eat", "drink", "sleep", "wake", "read", "write", "call", "go",
    "come", "walk", "run", "sit", "stand", "play", "study", "like",
    "love", "hate", "want", "need", "help", "give", "find", "buy", "make",
}
_FALLBACK_COPULAS = {"is", "am", "are", "was", "were", "be", "been", "being"}


def _heuristic_roles(text: str) -> Dict[str, Any]:
    clean = re.sub(r"[\.,!?;:'\"]", "", text.lower()).strip()
    tokens = [token for token in clean.split() if token]
    roles = {
        "subject": [],
        "verb": [],
        "object": [],
        "indirect_object": [],
        "time": [],
        "location": [],
        "modifier": [],
        "negation": [],
        "auxiliary": [],
    }

    stop_words = {"the", "a", "an", "my", "your", "our", "their", "please", "to", "at", "in", "on"}
    is_question = bool(tokens and tokens[0] in _FALLBACK_QUESTION_WORDS) or text.rstrip().endswith("?")
    has_negation = any(token in _FALLBACK_NEGATION_WORDS for token in tokens)

    if has_negation:
        roles["negation"] = [token for token in tokens if token in _FALLBACK_NEGATION_WORDS]

    for token in tokens:
        if token in _FALLBACK_TIME_WORDS:
            roles["time"].append(token)
        elif token in _FALLBACK_LOCATION_WORDS:
            roles["location"].append(token)
        elif token in _FALLBACK_COPULAS:
            roles["auxiliary"].append(token)

    if tokens and tokens[0] == "please" and any(token in _FALLBACK_ACTION_WORDS for token in tokens):
        roles["subject"].append("you")

    verb = next((token for token in tokens if token in _FALLBACK_ACTION_WORDS or token.endswith("ing") or token.endswith("ed")), None)
    if verb:
        roles["verb"].append(verb)

    subject = None
    if roles["subject"]:
        subject = roles["subject"][0]
    else:
        for token in tokens:
            if token in _FALLBACK_QUESTION_WORDS or token in stop_words or token in _FALLBACK_COPULAS or token in _FALLBACK_ACTION_WORDS or token in _FALLBACK_TIME_WORDS or token in _FALLBACK_LOCATION_WORDS:
                continue
            if token in _FALLBACK_SUBJECT_PRONOUNS:
                subject = token
                break
            if token not in _FALLBACK_OBJECT_PRONOUNS:
                subject = token
                break

    if subject:
        roles["subject"].append(subject)

    for token in tokens:
        if token in _FALLBACK_OBJECT_PRONOUNS:
            roles["indirect_object"].append(token)
            continue

        if token in roles["time"] or token in roles["location"] or token in roles["negation"] or token in roles["auxiliary"]:
            continue
        if token in _FALLBACK_QUESTION_WORDS or token in stop_words or token == subject or token == verb:
            continue
        if token not in roles["object"]:
            roles["object"].append(token)

    for token in tokens:
        if token in roles["time"] or token in roles["location"] or token in roles["negation"] or token in roles["auxiliary"] or token in roles["subject"] or token in roles["verb"] or token in roles["object"] or token in roles["indirect_object"]:
            continue
        if token not in stop_words and token not in _FALLBACK_QUESTION_WORDS:
            roles["modifier"].append(token)

    if is_question and not roles["location"] and roles["object"]:
        roles["location"] = roles["object"][:]
        roles["object"] = []

    return {
        "semantic_roles": roles,
        "is_question": is_question,
        "has_negation": has_negation,
    }


# ---------------------------------------------------------------------------
# Token-level helpers (lightweight, no spaCy needed)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> List[Dict[str, str]]:
    """Very simple whitespace tokenizer that returns token dicts."""
    tokens = []
    for word in text.split():
        clean = word.strip(".,!?;:\"'")
        if clean:
            tokens.append({
                "text": clean,
                "lemma": clean.lower(),
                "pos": "NOUN",   # unknown without a tagger
                "tag": "NN",
                "dep": "dep",
                "head": clean,
                "is_stop": False,
            })
    return tokens


# ---------------------------------------------------------------------------
# Fallback analyzer (no model available)
# ---------------------------------------------------------------------------

_NEG_WORDS  = {"not", "no", "never", "none", "n't"}
_TIME_WORDS = {
    "yesterday", "today", "tomorrow", "morning", "afternoon",
    "evening", "night", "now", "later", "soon",
}
_PRONOUNS   = {"i", "you", "he", "she", "we", "they", "it"}
_LOC_WORDS  = {"home", "work", "office", "park", "school", "store", "hospital", "market"}


def _fallback_analyze(text: str) -> Dict[str, Any]:
    words = [w.strip(".,!?;:") for w in text.lower().split() if w.strip()]
    roles: Dict[str, List[str]] = {
        "subject": [], "verb": [], "object": [], "indirect_object": [],
        "time": [], "location": [], "negation": [], "auxiliary": [], "modifier": [],
    }
    for w in words:
        if w in _NEG_WORDS:
            roles["negation"].append(w)
        elif w in _TIME_WORDS:
            roles["time"].append(w)
        elif w in _PRONOUNS:
            roles["subject"].append(w)
        elif w in _LOC_WORDS:
            roles["location"].append(w)
        elif w.endswith("ing") or w.endswith("ed"):
            if w not in roles["verb"]:
                roles["verb"].append(w)
        else:
            if w not in roles["object"]:
                roles["object"].append(w)

    return {
        "original_text": text,
        "tokens": _tokenize(text),
        "entities": [],
        "semantic_roles": roles,
        "is_question": text.strip().endswith("?"),
        "tense": "unknown",
        "aspect": "unknown",
        "has_negation": bool(roles["negation"]),
        "model_used": "fallback-rule-based",
        "analysis_timestamp": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Main analyzer class
# ---------------------------------------------------------------------------

class SemanticAnalyzer:
    """
    Wraps Flan-T5 (google/flan-t5-base) to perform structured semantic role
    labelling via instruction-following prompts.

    Falls back to a lightweight rule-based analyzer when the model is
    unavailable (e.g. no internet / insufficient RAM).
    """

    def __init__(self, model_name: str = "google/flan-t5-base"):
        self.model_name = model_name
        # Eagerly attempt to warm up the model so the first request is faster
        self._pipe = _get_pipeline()

    # ------------------------------------------------------------------
    # Tense / aspect helpers (rule-based, no model needed)
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_tense_from_text(text: str) -> str:
        lower = text.lower()
        if any(w in lower for w in ["will ", "shall ", "going to"]):
            return "future"
        if any(w in lower for w in ["would ", "could ", "might ", "should "]):
            return "conditional"
        if any(w in lower for w in ["was ", "were ", " had ", " did "]):
            return "past"
        if any(w in lower for w in [" is ", " am ", " are ", " do ", " does "]):
            return "present"
        return "unknown"

    @staticmethod
    def _detect_aspect_from_text(text: str) -> str:
        lower = text.lower()
        if re.search(r"\b(is|am|are|was|were)\b.*\b\w+ing\b", lower):
            return "progressive"
        if re.search(r"\b(have|has|had)\b", lower):
            return "perfective"
        return "habitual"

    # ------------------------------------------------------------------
    # Core analysis
    # ------------------------------------------------------------------

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Run Flan-T5 semantic analysis on *text*.
        Falls back to rule-based if the model is unavailable.
        """
        if self._pipe is None:
            self._pipe = _get_pipeline()

        if self._pipe is None:
            logger.warning("Flan-T5 unavailable — using rule-based fallback.")
            return _fallback_analyze(text)

        prompt = PROMPT_TEMPLATE.format(sentence=text)

        try:
            result = self._pipe(prompt, do_sample=False)[0]["generated_text"]
            roles, is_question, has_negation = _parse_flan_output(result)
        except Exception as e:
            logger.error(f"Flan-T5 inference error: {e}; falling back.")
            return _fallback_analyze(text)

        if not any(len(value) > 0 for value in roles.values()):
            fallback = _heuristic_roles(text)
            roles = fallback["semantic_roles"]
            is_question = is_question or fallback["is_question"]
            has_negation = has_negation or fallback["has_negation"]

        is_question = is_question or text.rstrip().endswith("?")

        tense  = self._detect_tense_from_text(text)
        aspect = self._detect_aspect_from_text(text)

        return {
            "original_text": text,
            "tokens": _tokenize(text),
            "entities": [],
            "semantic_roles": roles,
            "is_question": is_question,
            "tense": tense,
            "aspect": aspect,
            "has_negation": has_negation,
            "model_used": self.model_name,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }


# ---------------------------------------------------------------------------
# Module-level singletons (used by translation_service via `from analyzer import analyzer`)
# ---------------------------------------------------------------------------

_analyzer: Optional[SemanticAnalyzer] = None


def get_analyzer() -> SemanticAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = SemanticAnalyzer(model_name="google/flan-t5-base")
    return _analyzer


def analyze_text(text: str) -> Dict[str, Any]:
    return get_analyzer().analyze(text)


# Singleton instance imported directly by translation_service
analyzer = SemanticAnalyzer()
