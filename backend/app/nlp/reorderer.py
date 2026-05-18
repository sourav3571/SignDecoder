
from typing import Dict, List, Any, Set
import logging

logger = logging.getLogger(__name__)

FUNCTION_WORDS_TO_DROP = {

    "a", "an", "the",

    "is", "am", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "doing",
    "have", "has", "had", "having",
    "will", "would", "shall", "should",
    "may", "might", "can", "could", "must",

    "to", "at", "in", "on", "from", "with", "by", "about", "for", "of", "or",

    "and", "but", "or", "yet", "so",

    "i", "you", "he", "she", "it", "we", "they",

    "that", "which", "who", "whom", "what", "where", "when", "why", "how",
}

class SignLanguageReorderer:

    def __init__(self, sign_language: str = "ASL"):

        self.sign_language = sign_language
        logger.info(f"SignLanguageReorderer initialized for {sign_language}")

    def _filter_function_words(self, words: List[str]) -> List[str]:

        return [w for w in words if w.lower() not in FUNCTION_WORDS_TO_DROP]

    def _deduplicate_preserve_order(self, words: List[str]) -> List[str]:

        seen: Set[str] = set()
        result = []
        for word in words:
            if word not in seen:
                result.append(word)
                seen.add(word)
        return result

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
        auxiliary_roles = semantic_roles.get("auxiliary", [])

        time_gloss = self._filter_function_words(time_roles)
        time_gloss = self._deduplicate_preserve_order(time_gloss)

        location_gloss = self._filter_function_words(location_roles)
        location_gloss = self._deduplicate_preserve_order(location_gloss)

        subject_gloss = self._filter_function_words(subject_roles)
        subject_gloss = self._deduplicate_preserve_order(subject_gloss)

        object_gloss = self._filter_function_words(object_roles)
        object_gloss = self._deduplicate_preserve_order(object_gloss)

        verb_gloss = self._filter_function_words(verb_roles)
        verb_gloss = self._deduplicate_preserve_order(verb_gloss)

        modifier_gloss = self._filter_function_words(modifier_roles)
        modifier_gloss = self._deduplicate_preserve_order(modifier_gloss)

        if is_question:

            question_marker = ["QUESTION"]
        else:
            question_marker = []

        if has_negation:
            negation_marker = ["NOT"] if not negation_roles else negation_roles
        else:
            negation_marker = []

        reordered_gloss = (
            time_gloss +
            location_gloss +
            subject_gloss +
            object_gloss +
            verb_gloss +
            modifier_gloss +
            negation_marker +
            question_marker
        )

        reordered_gloss = [g for g in reordered_gloss if g]

        reordered_gloss = [g.upper() for g in reordered_gloss]

        grammatical_structure = {
            "time": time_gloss,
            "location": location_gloss,
            "topic": subject_gloss,
            "focus": object_gloss,
            "action": verb_gloss,
            "modifier": modifier_gloss,
            "negation": negation_marker,
            "question": is_question,
        }

        return {
            "original_text": analysis.get("original_text", ""),
            "semantic_roles": semantic_roles,
            "reordered_gloss": reordered_gloss,
            "gloss_string": " ".join(reordered_gloss),
            "grammatical_structure": grammatical_structure,
            "sign_language": self.sign_language,
            "is_question": is_question,
            "has_negation": has_negation,
        }

_reorderer: SignLanguageReorderer = SignLanguageReorderer(sign_language="ASL")

def reorder_for_sign_language(analysis: Dict[str, Any]) -> Dict[str, Any]:

    return _reorderer.reorder(analysis)
