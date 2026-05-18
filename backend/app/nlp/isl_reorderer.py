from typing import Dict, List, Any, Set, Tuple
import logging

logger = logging.getLogger(__name__)

ISL_FUNCTION_WORDS_TO_DROP = {

    "a", "an", "the",

    "is", "am", "are", "was", "were", "be", "been", "being",
    "do", "does", "did",
    "have", "has", "had",
    "will", "would", "shall", "should",
    "may", "might", "can", "could", "must",

    "to", "at", "in", "on", "from", "with", "by", "about",
    "for", "of", "or", "up", "down", "out", "back",

    "and", "but", "or", "yet", "so", "because",

    "be",

    "i", "you", "he", "she", "it", "we", "they",

    "that", "which", "who", "whom", "what", "where", "when", "why", "how",
}

ISL_TIME_MARKERS = {

    "yesterday": {"isl_gloss": "YESTERDAY", "tense": "past", "specificity": "specific"},
    "ago": {"isl_gloss": "AGO", "tense": "past", "specificity": "relative"},
    "before": {"isl_gloss": "BEFORE-TIME", "tense": "past", "specificity": "relative"},
    "last": {"isl_gloss": "LAST", "tense": "past", "specificity": "relative"},

    "today": {"isl_gloss": "TODAY", "tense": "present", "specificity": "specific"},
    "now": {"isl_gloss": "NOW", "tense": "present", "specificity": "present-moment"},
    "currently": {"isl_gloss": "NOW-ONGOING", "tense": "present", "specificity": "ongoing"},

    "tomorrow": {"isl_gloss": "TOMORROW", "tense": "future", "specificity": "specific"},
    "next": {"isl_gloss": "NEXT", "tense": "future", "specificity": "relative"},
    "later": {"isl_gloss": "LATER", "tense": "future", "specificity": "relative"},
    "will": {"isl_gloss": "FUTURE", "tense": "future", "specificity": "future-marker"},
}

ISL_LOCATION_MARKERS = {
    "home": {"isl_gloss": "HOME", "spatial_position": "center-neutral", "type": "building"},
    "school": {"isl_gloss": "SCHOOL", "spatial_position": "center-neutral", "type": "building"},
    "office": {"isl_gloss": "OFFICE", "spatial_position": "center-neutral", "type": "building"},
    "hospital": {"isl_gloss": "HOSPITAL", "spatial_position": "center-neutral", "type": "building"},
    "market": {"isl_gloss": "MARKET", "spatial_position": "center-neutral", "type": "location"},
    "park": {"isl_gloss": "PARK", "spatial_position": "center-neutral", "type": "location"},
    "road": {"isl_gloss": "ROAD", "spatial_position": "horizontal", "type": "location"},
    "here": {"isl_gloss": "HERE", "spatial_position": "proximal", "type": "proximal"},
    "there": {"isl_gloss": "THERE", "spatial_position": "distal", "type": "distal"},
    "up": {"isl_gloss": "UP", "spatial_position": "superior", "type": "direction"},
    "down": {"isl_gloss": "DOWN", "spatial_position": "inferior", "type": "direction"},
}

ISL_VERB_TYPES = {

    "plain": ["want", "like", "think", "know", "remember", "forget"],

    "spatial": ["go", "come", "put", "place", "move", "throw", "take"],

    "classifier": ["drive", "walk", "fly", "swim", "jump", "sit", "stand"],

    "directional": ["give", "send", "tell", "ask", "show", "help"],

    "depicting": ["eat", "drink", "write", "read", "carry"],
}

class ISLReorderer:

    def __init__(self, sign_language: str = "ISL"):

        if sign_language != "ISL":
            logger.warning(f"ISLReorderer expects 'ISL' but got '{sign_language}'")
        self.sign_language = sign_language
        self.time_markers = ISL_TIME_MARKERS
        self.location_markers = ISL_LOCATION_MARKERS
        self.verb_types = ISL_VERB_TYPES
        logger.info(f"ISLReorderer initialized for {sign_language}")

    def _filter_function_words(self, words: List[str]) -> List[str]:

        return [w for w in words if w.lower() not in ISL_FUNCTION_WORDS_TO_DROP]

    def _deduplicate_preserve_order(self, words: List[str]) -> List[str]:

        seen: Set[str] = set()
        result = []
        for word in words:
            if word not in seen:
                result.append(word)
                seen.add(word)
        return result

    def _get_time_marking(self, time_roles: List[str]) -> Tuple[List[str], str]:

        time_gloss = []
        detected_tense = "present"  

        for word in time_roles:
            word_lower = word.lower()
            if word_lower in ISL_TIME_MARKERS:
                marker = ISL_TIME_MARKERS[word_lower]
                time_gloss.append(marker["isl_gloss"])
                detected_tense = marker["tense"]

        return self._deduplicate_preserve_order(time_gloss), detected_tense

    def _get_location_marking(self, location_roles: List[str]) -> Tuple[List[str], List[Dict]]:

        location_gloss = []
        spatial_info = []

        for word in location_roles:
            word_lower = word.lower()
            if word_lower in ISL_LOCATION_MARKERS:
                marker = ISL_LOCATION_MARKERS[word_lower]
                location_gloss.append(marker["isl_gloss"])
                spatial_info.append({
                    "word": word,
                    "position": marker["spatial_position"],
                    "type": marker["type"]
                })

        return self._deduplicate_preserve_order(location_gloss), spatial_info

    def _classify_verb(self, verb: str) -> str:

        verb_lower = verb.lower()
        for verb_type, verbs in ISL_VERB_TYPES.items():
            if verb_lower in verbs:
                return verb_type
        return "plain"  

    def reorder(self, analysis: Dict[str, Any]) -> Dict[str, Any]:

        semantic_roles = analysis.get("semantic_roles", {})
        is_question = analysis.get("is_question", False)
        has_negation = analysis.get("has_negation", False)

        time_roles = semantic_roles.get("time", [])
        location_roles = semantic_roles.get("location", [])
        subject_roles = semantic_roles.get("subject", [])
        object_roles = semantic_roles.get("object", [])
        verb_roles = semantic_roles.get("verb", [])
        negation_roles = semantic_roles.get("negation", [])
        modifier_roles = semantic_roles.get("modifier", [])

        time_gloss, detected_tense = self._get_time_marking(time_roles)

        location_gloss, spatial_info = self._get_location_marking(location_roles)

        subject_gloss = self._filter_function_words(subject_roles)
        subject_gloss = self._deduplicate_preserve_order(subject_gloss)

        object_gloss = self._filter_function_words(object_roles)
        object_gloss = self._deduplicate_preserve_order(object_gloss)

        verb_gloss = self._filter_function_words(verb_roles)
        verb_gloss = self._deduplicate_preserve_order(verb_gloss)
        verb_type = self._classify_verb(verb_gloss[0]) if verb_gloss else "plain"

        modifier_gloss = self._filter_function_words(modifier_roles)
        modifier_gloss = self._deduplicate_preserve_order(modifier_gloss)

        question_marker = []
        negation_marker = []

        if is_question:
            question_marker = ["QUESTION"]  

        if has_negation:
            negation_marker = ["NOT"]  

        reordered_gloss = (
            time_gloss
            + location_gloss
            + subject_gloss
            + object_gloss
            + verb_gloss
            + modifier_gloss
            + negation_marker
            + question_marker
        )

        gloss_string = " ".join(reordered_gloss)

        grammatical_structure = {
            "temporal": {
                "gloss": time_gloss,
                "tense": detected_tense,
                "marked": len(time_gloss) > 0
            },
            "spatial": {
                "gloss": location_gloss,
                "locations": spatial_info,
                "marked": len(location_gloss) > 0
            },
            "topic": {
                "gloss": subject_gloss,
                "marked": len(subject_gloss) > 0
            },
            "focus": {
                "gloss": object_gloss,
                "marked": len(object_gloss) > 0
            },
            "action": {
                "gloss": verb_gloss,
                "verb_type": verb_type,
                "marked": len(verb_gloss) > 0
            },
            "modifiers": {
                "gloss": modifier_gloss,
                "marked": len(modifier_gloss) > 0
            },
            "negation": {
                "gloss": negation_marker,
                "marked": len(negation_marker) > 0
            },
            "question": {
                "gloss": question_marker,
                "marked": is_question
            }
        }

        isl_metadata = {
            "sign_language": "ISL",
            "tense": detected_tense,
            "verb_type": verb_type,
            "spatial_complexity": len(spatial_info),
            "facial_expressions_required": ["brow_raise"] if is_question else [],
            "requires_role_shift": any("role" in str(s).lower() for s in semantic_roles.values())
        }

        return {
            "original_text": analysis.get("original_text", ""),
            "semantic_roles": semantic_roles,
            "reordered_gloss": reordered_gloss,
            "gloss_string": gloss_string,
            "grammatical_structure": grammatical_structure,
            "isl_metadata": isl_metadata
        }

isl_reorderer = ISLReorderer(sign_language="ISL")
