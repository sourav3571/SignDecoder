"""
Sign Language Grammar Reorderer

Transforms English SVO (Subject-Verb-Object) word order into
sign language SOV (Subject-Object-Verb) order with specific rules.

Core Principle:
  Sign languages do NOT follow English word order.
  Instead, they use a Topic-Comment structure with specific positioning rules.

Sign Language Grammar Rules:
  1. TIME FIRST — when did this happen? (temporal orientation)
  2. LOCATION SECOND — where did this happen? (spatial orientation)
  3. SUBJECT — who did it? (topic)
  4. OBJECT — what/whom? (focus)
  5. VERB — the action (comment)
  6. NEGATION — marked at end for emphasis, or beginning for focus
  7. QUESTION — question mark, or WH-word at beginning

Example Transformation:
  English: "I ate pizza at home yesterday"
  → Analysis: WHO=I, VERB=eat, WHAT=pizza, WHERE=home, WHEN=yesterday
  → Sign order: YESTERDAY HOME I PIZZA EAT
  → Emoji: ⬅️📅 🏠 👤 🍕 🍽️

Research Note:
  Different sign languages have slight variations:
  - ASL (American Sign Language)
  - BSL (British Sign Language)
  - LSF (French Sign Language)
  
  For this project, we implement ASL rules as baseline.
  Can be extended with other sign language rules.
"""

from typing import Dict, List, Any, Set
import logging

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════
# Function Words to Remove
# ════════════════════════════════════════════════════════════════════

# These words are typically dropped in sign language as they're conveyed through other means
# (e.g., verb agreement, spatial modulation, classifier handshapes)
FUNCTION_WORDS_TO_DROP = {
    # Articles
    "a", "an", "the",
    # Auxiliary verbs (tense/aspect conveyed through other means in sign language)
    "is", "am", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "doing",
    "have", "has", "had", "having",
    "will", "would", "shall", "should",
    "may", "might", "can", "could", "must",
    # Prepositions (often conveyed through spatial modulation)
    "to", "at", "in", "on", "from", "with", "by", "about", "for", "of", "or",
    # Conjunctions
    "and", "but", "or", "yet", "so",
    # Personal pronouns (role shifting in sign language)
    "i", "you", "he", "she", "it", "we", "they",
    # Relative pronouns and question words
    "that", "which", "who", "whom", "what", "where", "when", "why", "how",
}


class SignLanguageReorderer:
    """
    Reorders English words according to sign language grammar rules.
    
    Sign Language Structure (ASL):
      TOPIC (establishes context) + COMMENT (describes action)
      
      Context = Time + Location + Topic
      Action = Object + Verb + Negation/Question
    """
    
    def __init__(self, sign_language: str = "ASL"):
        """
        Initialize reorderer.
        
        Args:
            sign_language: Which sign language rules to use
                          - "ASL" (American Sign Language) - default
                          - Others can be added later
        """
        self.sign_language = sign_language
        logger.info(f"SignLanguageReorderer initialized for {sign_language}")
    
    def _filter_function_words(self, words: List[str]) -> List[str]:
        """
        Remove function words that are typically dropped in sign language.
        
        Args:
            words: List of lemmas
            
        Returns:
            Filtered list without function words
        """
        return [w for w in words if w.lower() not in FUNCTION_WORDS_TO_DROP]
    
    def _deduplicate_preserve_order(self, words: List[str]) -> List[str]:
        """Remove duplicates while preserving order."""
        seen: Set[str] = set()
        result = []
        for word in words:
            if word not in seen:
                result.append(word)
                seen.add(word)
        return result
    
    def reorder(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reorder words according to sign language grammar.
        
        Args:
            analysis: Output from SemanticAnalyzer with semantic_roles extracted
            
        Returns:
            {
                "original_text": "I ate pizza at home yesterday",
                "semantic_roles": {...},
                "reordered_gloss": ["YESTERDAY", "HOME", "I", "PIZZA", "EAT"],
                "gloss_string": "YESTERDAY HOME I PIZZA EAT",
                "grammatical_structure": {
                    "time": ["YESTERDAY"],
                    "location": ["HOME"],
                    "topic": ["I"],
                    "focus": ["PIZZA"],
                    "action": ["EAT"],
                    "negation": [],
                    "question": false
                }
            }
        """
        
        semantic_roles = analysis.get("semantic_roles", {})
        is_question = analysis.get("is_question", False)
        has_negation = analysis.get("has_negation", False)
        
        # ──────────────────────────────────────────────────────────────
        # Extract semantic role components
        # ──────────────────────────────────────────────────────────────
        
        time_roles = semantic_roles.get("time", [])
        location_roles = semantic_roles.get("location", [])
        subject_roles = semantic_roles.get("subject", [])
        object_roles = semantic_roles.get("object", [])
        verb_roles = semantic_roles.get("verb", [])
        negation_roles = semantic_roles.get("negation", [])
        modifier_roles = semantic_roles.get("modifier", [])
        auxiliary_roles = semantic_roles.get("auxiliary", [])
        
        # ──────────────────────────────────────────────────────────────
        # Rule 1: TIME FIRST
        # ──────────────────────────────────────────────────────────────
        time_gloss = self._filter_function_words(time_roles)
        time_gloss = self._deduplicate_preserve_order(time_gloss)
        
        # ──────────────────────────────────────────────────────────────
        # Rule 2: LOCATION SECOND
        # ──────────────────────────────────────────────────────────────
        location_gloss = self._filter_function_words(location_roles)
        location_gloss = self._deduplicate_preserve_order(location_gloss)
        
        # ──────────────────────────────────────────────────────────────
        # Rule 3: SUBJECT (Topic)
        # ──────────────────────────────────────────────────────────────
        subject_gloss = self._filter_function_words(subject_roles)
        subject_gloss = self._deduplicate_preserve_order(subject_gloss)
        
        # ──────────────────────────────────────────────────────────────
        # Rule 4: OBJECT (Focus/Patient)
        # ──────────────────────────────────────────────────────────────
        object_gloss = self._filter_function_words(object_roles)
        object_gloss = self._deduplicate_preserve_order(object_gloss)
        
        # ──────────────────────────────────────────────────────────────
        # Rule 5: VERB (Action/Comment)
        # ──────────────────────────────────────────────────────────────
        verb_gloss = self._filter_function_words(verb_roles)
        verb_gloss = self._deduplicate_preserve_order(verb_gloss)
        
        # ──────────────────────────────────────────────────────────────
        # Rule 6: MODIFIERS (Adjectives, Adverbial modifiers)
        # Apply after verb but before negation
        # ──────────────────────────────────────────────────────────────
        modifier_gloss = self._filter_function_words(modifier_roles)
        modifier_gloss = self._deduplicate_preserve_order(modifier_gloss)
        
        # ──────────────────────────────────────────────────────────────
        # Rule 7: NEGATION or QUESTION
        # ──────────────────────────────────────────────────────────────
        
        if is_question:
            # Question structure: statement + QUESTION (often PRO.Q or specific WH-word)
            # WH-words go at the beginning in some sign languages
            question_marker = ["QUESTION"]
        else:
            question_marker = []
        
        if has_negation:
            negation_marker = ["NOT"] if not negation_roles else negation_roles
        else:
            negation_marker = []
        
        # ──────────────────────────────────────────────────────────────
        # Build final gloss sequence: ASL/Sign Language order
        # ──────────────────────────────────────────────────────────────
        # CONTEXT (Topic-setting): Time + Location + Subject
        # ACTION (Comment): Object + Verb + Modifiers + Negation + Question
        
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
        
        # Remove empty strings
        reordered_gloss = [g for g in reordered_gloss if g]
        
        # Convert to uppercase (sign language convention)
        reordered_gloss = [g.upper() for g in reordered_gloss]
        
        # ──────────────────────────────────────────────────────────────
        # Build grammatical structure for reference
        # ──────────────────────────────────────────────────────────────
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


# ════════════════════════════════════════════════════════════════════
# Singleton instance
# ════════════════════════════════════════════════════════════════════

_reorderer: SignLanguageReorderer = SignLanguageReorderer(sign_language="ASL")


def reorder_for_sign_language(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function for sign language reordering.
    
    Usage:
        analysis = analyze_text("I ate pizza at home yesterday")
        reordered = reorder_for_sign_language(analysis)
        print(reordered["gloss_string"])  # "YESTERDAY HOME I PIZZA EAT"
    """
    return _reorderer.reorder(analysis)
