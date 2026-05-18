"""
Text Preprocessor Module

Cleans and normalizes input text before NLP analysis:
  • Spell checking (SymSpell)
  • Contraction expansion (I'm → I am)
  • Whitespace normalization
  • Special character handling
  • Lowercase conversion
  • Emoji/URL removal

Purpose:
  Ensure consistent, clean input for downstream NLP modules.
  Spacy models perform better with normalized text.

Research note:
  Text quality directly impacts NLP accuracy. Document preprocessing
  as part of ablation studies to show its contribution.
"""

import re
from typing import Dict, List, Tuple, Optional
from symspellpy import SymSpell, Verbosity
import logging

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════
# Contraction Mappings
# ════════════════════════════════════════════════════════════════════
CONTRACTION_MAP = {
    # Negations
    "ain't": "am not",
    "aren't": "are not",
    "can't": "cannot",
    "can't've": "cannot have",
    "couldn't": "could not",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hasn't": "has not",
    "haven't": "have not",
    "isn't": "is not",
    "shouldn't": "should not",
    "wasn't": "was not",
    "weren't": "were not",
    "won't": "will not",
    "wouldn't": "would not",
    # Contractions
    "i'd": "i would",
    "i'll": "i will",
    "i'm": "i am",
    "i've": "i have",
    "he'd": "he would",
    "he'll": "he will",
    "he's": "he is",
    "she'd": "she would",
    "she'll": "she will",
    "she's": "she is",
    "that's": "that is",
    "there's": "there is",
    "they'd": "they would",
    "they'll": "they will",
    "they're": "they are",
    "they've": "they have",
    "we'd": "we would",
    "we'll": "we will",
    "we're": "we are",
    "we've": "we have",
    "what's": "what is",
    "where's": "where is",
    "who's": "who is",
    "it's": "it is",
    "let's": "let us",
    "that'd": "that would",
    "who'd": "who would",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all're": "you all are",
    "y'all've": "you all have",
    # Slang
    "gonna": "going to",
    "wanna": "want to",
    "gotta": "got to",
    "lemme": "let me",
    "kinda": "kind of",
    "sorta": "sort of",
}


class TextPreprocessor:
    """
    Preprocess text for NLP analysis.
    
    Pipeline:
      1. Remove URLs and emails
      2. Remove emojis
      3. Expand contractions
      4. Normalize whitespace
      5. Spell check (optional, slower)
      6. Lowercase
      7. Remove extra punctuation
    
    Performance: ~100ms for typical sentence
    """
    
    def __init__(self, use_spell_check: bool = False):
        """
        Initialize preprocessor.
        
        Args:
            use_spell_check: Enable SymSpell spell checking (slower, optional for Phase 2)
                            Disable for speed; enable after Phase 3 if needed
        """
        self.use_spell_check = use_spell_check
        self.spell_checker: Optional[SymSpell] = None
        
        if use_spell_check:
            try:
                self.spell_checker = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
                logger.info("Spell checker initialized")
            except Exception as e:
                logger.warning(f"Spell checker initialization failed: {e}. Continuing without it.")
                self.use_spell_check = False
    
    def expand_contractions(self, text: str) -> str:
        """
        Expand contractions (I'm → I am).
        
        Args:
            text: Input text with contractions
            
        Returns:
            Text with contractions expanded
        """
        pattern = re.compile(r'\b(' + '|'.join(CONTRACTION_MAP.keys()) + r')\b', re.IGNORECASE)
        
        def replace(match):
            return CONTRACTION_MAP[match.group(0).lower()]
        
        return pattern.sub(replace, text)
    
    def remove_urls_emails(self, text: str) -> str:
        """Remove URLs and email addresses."""
        # Remove URLs
        text = re.compile(r'http\S+|www\S+|https\S+', re.MULTILINE).sub('', text)
        # Remove emails
        text = re.sub(r'\S+@\S+', '', text)
        return text
    
    def remove_emojis(self, text: str) -> str:
        """Remove emoji characters."""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F700-\U0001F77F"
            "\U0001F780-\U0001F7FF"
            "\U0001F800-\U0001F8FF"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FA6F"
            "\U0001FA70-\U0001FAFF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"
            "\u3030"
            "]+"
        )
        return emoji_pattern.sub(r'', text)
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace.
        
        - Convert tabs to spaces
        - Remove leading/trailing whitespace
        - Collapse multiple spaces to single space
        """
        text = text.replace('\t', ' ')
        text = ' '.join(text.split())  # Collapse multiple spaces
        return text.strip()
    
    def remove_extra_punctuation(self, text: str) -> str:
        """Remove repeated punctuation (... → ., ??? → ?)."""
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\?{2,}', '?', text)
        text = re.sub(r'!{2,}', '!', text)
        return text
    
    def preprocess(
        self,
        text: str,
        include_original: bool = False
    ) -> Dict[str, str]:
        """
        Full preprocessing pipeline.
        
        Args:
            text: Raw input text
            include_original: Return both original and processed
            
        Returns:
            {
                "original": "I'm eating pizza",
                "processed": "i am eating pizza",
                "preprocessing_steps": ["expanded_contractions", "normalized_whitespace", ...]
            }
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        original = text
        steps = []
        
        # Step 1: Remove URLs and emails
        text = self.remove_urls_emails(text)
        if text != original:
            steps.append("removed_urls_emails")
        
        # Step 2: Remove emojis
        original_len = len(text)
        text = self.remove_emojis(text)
        if len(text) < original_len:
            steps.append("removed_emojis")
        
        # Step 3: Expand contractions
        original = text
        text = self.expand_contractions(text)
        if text != original:
            steps.append("expanded_contractions")
        
        # Step 4: Normalize whitespace
        original = text
        text = self.normalize_whitespace(text)
        if text != original:
            steps.append("normalized_whitespace")
        
        # Step 5: Remove extra punctuation
        original = text
        text = self.remove_extra_punctuation(text)
        if text != original:
            steps.append("removed_extra_punctuation")
        
        # Step 6: Lowercase (do this last to preserve intent)
        text = text.lower()
        steps.append("lowercased")
        
        result = {
            "processed": text,
            "preprocessing_steps": steps,
        }
        
        if include_original:
            result["original"] = original
        
        return result

    def clean_text(self, text: str) -> str:
        """Return the preprocessed text string."""
        return self.preprocess(text)["processed"]


# ════════════════════════════════════════════════════════════════════════════
# Singleton instance
# ════════════════════════════════════════════════════════════════════════════

_preprocessor = TextPreprocessor(use_spell_check=False)
preprocessor = _preprocessor


def preprocess_text(text: str, include_original: bool = False) -> Dict[str, str]:
    """
    Quick preprocessing function.
    
    Usage:
        result = preprocess_text("I'm eating pizza at home!")
        print(result["processed"])  # "i am eating pizza at home"
    """
    return _preprocessor.preprocess(text, include_original=include_original)
