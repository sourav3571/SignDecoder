"""
Gloss Generator Module

Generates Sign Language Gloss - the textual representation of sign language.

Gloss Definition:
  A written representation of sign language using capitalized English words
  or special symbols to represent signs and linguistic phenomena.
  
  Example:
    Input: "I ate pizza"
    Gloss: "I PIZZA EAT"
    
    Note: Glosses are NOT translations; they represent the structure
    and flow of signed information.

Hybrid Approach:
  Phase 2 (Current): Rule-based gloss generation using semantic reordering
  Phase 4 (Future): Fine-tuned T5 transformer model for better gloss quality
  
  Phase 2 uses the reordered words from SignLanguageReorderer.
  Phase 4 will learn gloss patterns from PHOENIX dataset (ASL corpus).

Gloss Conventions:
  • All signs in CAPS: PERSON, WALK, HAPPY
  • Special markers:
    - PRO1 / PRO2 / PRO3 for pronouns (spatial)
    - NEGATION / NOT for negation
    - WH-QUESTION mark for questions
    - ^ for classifier predicates
    - ~ for repetition/duration
  • Verb agreement: GIVE-1S (give to 1st person singular)
  • Classifiers: CL:person, CL:vehicle, etc.

Research Note:
  Gloss generation quality is measured by BLEU score against
  PHOENIX corpus. Document improvements at each phase.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GlossGenerator:
    """
    Generates Sign Language Gloss from reordered semantic analysis.
    
    Phase 2 Implementation: Rule-based approach
      Uses reordered words from SignLanguageReorderer directly.
      Applies gloss conventions and special markers.
    
    Phase 4 Enhancement: Add T5 transformer for better quality
    """
    
    def __init__(self, use_ml_model: bool = False):
        """
        Initialize gloss generator.
        
        Args:
            use_ml_model: Enable T5 transformer (Phase 4+)
                         Disabled by default for Phase 2
        """
        self.use_ml_model = use_ml_model
        self.t5_model = None
        self.t5_tokenizer = None
        
        if use_ml_model:
            self._load_t5()
    
    def _load_t5(self):
        """
        Load fine-tuned T5 model for English→Gloss translation.
        
        Note: This is for Phase 4. Not loaded by default in Phase 2.
        """
        try:
            from transformers import T5ForConditionalGeneration, T5Tokenizer
            
            logger.info("Loading T5 model for gloss generation...")
            # In Phase 4, this will be a fine-tuned checkpoint
            self.t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
            self.t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")
            logger.info("✓ T5 model loaded")
        except Exception as e:
            logger.warning(f"Failed to load T5 model: {e}")
            self.use_ml_model = False
    
    def _apply_gloss_conventions(self, word: str) -> str:
        """
        Apply sign language gloss conventions to a word.
        
        Conventions:
          • Capitalize all signs
          • Add markers for special linguistic features
          • Handle verb agreement
        
        Args:
            word: Word to glossify
            
        Returns:
            Glossified version of the word
        """
        # Capitalize
        gloss = word.upper()
        
        # Add gloss markers for special linguistic phenomena
        # These will be enriched as we add more analysis
        # For Phase 2, we keep it simple
        
        return gloss
    
    def _merge_multi_word_signs(self, glosses: List[str]) -> List[str]:
        """
        Merge related words into single multi-word signs.
        
        Example:
          ["GOOD", "MORNING"] → ["GOOD-MORNING"]
          ["PAST", "TENSE"] → ["PAST-TENSE"]
          
        This improves gloss readability and matches how signs are often
        represented in sign language corpora.
        """
        # Common multi-word signs in ASL
        multi_word_patterns = [
            (["GOOD", "MORNING"], "GOOD-MORNING"),
            (["GOOD", "NIGHT"], "GOOD-NIGHT"),
            (["THANK", "YOU"], "THANK-YOU"),
            (["SCHOOL", "WORK"], "SCHOOL-WORK"),
            (["GIRL", "FRIEND"], "GIRLFRIEND"),
            (["BOY", "FRIEND"], "BOYFRIEND"),
        ]
        
        merged = glosses.copy()
        
        for pattern, replacement in multi_word_patterns:
            i = 0
            while i < len(merged) - len(pattern) + 1:
                if merged[i:i+len(pattern)] == pattern:
                    merged = merged[:i] + [replacement] + merged[i+len(pattern):]
                    # Don't increment i, check again at this position
                else:
                    i += 1
        
        return merged
    
    def generate_rule_based(self, reordered_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate gloss using rule-based approach (Phase 2).
        
        Uses the reordered gloss from SignLanguageReorderer directly,
        applying gloss conventions and markers.
        
        Args:
            reordered_data: Output from SignLanguageReorderer
                           Contains reordered_gloss list
            
        Returns:
            {
                "gloss_string": "YESTERDAY HOME I PIZZA EAT",
                "gloss_list": ["YESTERDAY", "HOME", "I", "PIZZA", "EAT"],
                "confidence": 0.85,
                "method": "rule-based",
                "analysis": {...}
            }
        """
        
        reordered_gloss = reordered_data.get("reordered_gloss", [])
        
        # Apply gloss conventions
        glosses = [self._apply_gloss_conventions(word) for word in reordered_gloss]
        
        # Merge multi-word signs
        glosses = self._merge_multi_word_signs(glosses)
        
        # Add special markers for questions/negation
        if reordered_data.get("is_question"):
            glosses.append("QUESTION")
        
        if reordered_data.get("has_negation"):
            # Negation is often expressed through non-manual markers and word position
            # For gloss, we add NOT or NEGATION marker
            if "NOT" not in glosses:
                glosses.append("NOT")
        
        gloss_string = " ".join(glosses)
        
        # Confidence score for rule-based approach
        # Higher confidence = more confident in this gloss
        # Factors affecting confidence:
        #   - How many semantic roles were extracted (more = higher confidence)
        #   - Whether inputs were clear (no questions, negations = higher)
        confidence = self._calculate_confidence(reordered_data, glosses)
        
        return {
            "gloss_string": gloss_string,
            "gloss_list": glosses,
            "confidence": confidence,
            "method": "rule-based",
            "reordered_data": reordered_data,
        }
    
    def _calculate_confidence(self, reordered_data: Dict[str, Any], glosses: List[str]) -> float:
        """
        Calculate confidence score for generated gloss.
        
        Factors:
          • Number of semantic roles extracted (more = higher confidence)
          • Presence of uncertain phenomena (questions, negations = lower)
          • Original text complexity
          
        Returns:
          Float between 0.0 and 1.0
        """
        confidence = 0.5  # Baseline
        
        # Increase confidence based on semantic roles extracted
        semantic_roles = reordered_data.get("semantic_roles", {})
        roles_count = sum(1 for v in semantic_roles.values() if v)
        confidence += min(0.3, roles_count * 0.05)  # Up to +0.3
        
        # Decrease confidence for complex phenomena
        if reordered_data.get("is_question"):
            confidence -= 0.1
        if reordered_data.get("has_negation"):
            confidence -= 0.1
        
        # Increase confidence for longer, more complete glosses
        confidence += min(0.1, len(glosses) * 0.02)
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def generate_ml_based(self, text: str) -> Dict[str, Any]:
        """
        Generate gloss using T5 transformer model (Phase 4+).
        
        Note: Not implemented in Phase 2; stub for future phases.
        
        Args:
            text: Original English text
            
        Returns:
            ML-generated gloss with confidence score
        """
        if not self.use_ml_model or not self.t5_model:
            logger.warning("ML model not available; falling back to rule-based")
            return None
        
        try:
            # Prepare input for T5
            input_text = f"translate English to sign gloss: {text}"
            inputs = self.t5_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
            
            # Generate gloss
            outputs = self.t5_model.generate(
                inputs["input_ids"],
                max_length=128,
                num_beams=5,
                early_stopping=True,
            )
            
            gloss_string = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "gloss_string": gloss_string,
                "gloss_list": gloss_string.split(),
                "confidence": 0.75,  # T5 model confidence
                "method": "ml-based",
            }
        except Exception as e:
            logger.error(f"ML gloss generation failed: {e}")
            return None
    
    def generate(self, reordered_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate gloss using the best available method.
        
        Priority:
          1. T5 ML model (if enabled and loaded)
          2. Rule-based approach (default)
        
        Args:
            reordered_data: Output from SignLanguageReorderer
            
        Returns:
            Gloss generation result with confidence scores
        """
        # For Phase 2, always use rule-based approach
        return self.generate_rule_based(reordered_data)


# ════════════════════════════════════════════════════════════════════
# Singleton instance
# ════════════════════════════════════════════════════════════════════

_generator = GlossGenerator(use_ml_model=False)  # ML disabled in Phase 2


def generate_gloss(reordered_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function for gloss generation.
    
    Usage:
        reordered = reorder_for_sign_language(analysis)
        gloss_result = generate_gloss(reordered)
        print(gloss_result["gloss_string"])  # "YESTERDAY HOME I PIZZA EAT"
    """
    return _generator.generate(reordered_data)

# Singleton instance
gloss_generator = GlossGenerator()
