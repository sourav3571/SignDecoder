
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class GlossGenerator:

    def __init__(self, use_ml_model: bool = False):

        self.use_ml_model = use_ml_model
        self.t5_model = None
        self.t5_tokenizer = None

        if use_ml_model:
            self._load_t5()

    def _load_t5(self):

        try:
            from transformers import T5ForConditionalGeneration, T5Tokenizer

            logger.info("Loading T5 model for gloss generation...")

            self.t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
            self.t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")
            logger.info("✓ T5 model loaded")
        except Exception as e:
            logger.warning(f"Failed to load T5 model: {e}")
            self.use_ml_model = False

    def _apply_gloss_conventions(self, word: str) -> str:

        gloss = word.upper()

        return gloss

    def _merge_multi_word_signs(self, glosses: List[str]) -> List[str]:

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

                else:
                    i += 1

        return merged

    def generate_rule_based(self, reordered_data: Dict[str, Any]) -> Dict[str, Any]:

        reordered_gloss = reordered_data.get("reordered_gloss", [])

        glosses = [self._apply_gloss_conventions(word) for word in reordered_gloss]

        glosses = self._merge_multi_word_signs(glosses)

        if reordered_data.get("is_question"):
            glosses.append("QUESTION")

        if reordered_data.get("has_negation"):

            if "NOT" not in glosses:
                glosses.append("NOT")

        gloss_string = " ".join(glosses)

        confidence = self._calculate_confidence(reordered_data, glosses)

        return {
            "gloss_string": gloss_string,
            "gloss_list": glosses,
            "confidence": confidence,
            "method": "rule-based",
            "reordered_data": reordered_data,
        }

    def _calculate_confidence(self, reordered_data: Dict[str, Any], glosses: List[str]) -> float:

        confidence = 0.5  

        semantic_roles = reordered_data.get("semantic_roles", {})
        roles_count = sum(1 for v in semantic_roles.values() if v)
        confidence += min(0.3, roles_count * 0.05)  

        if reordered_data.get("is_question"):
            confidence -= 0.1
        if reordered_data.get("has_negation"):
            confidence -= 0.1

        confidence += min(0.1, len(glosses) * 0.02)

        return max(0.0, min(1.0, confidence))

    def generate_ml_based(self, text: str) -> Dict[str, Any]:

        if not self.use_ml_model or not self.t5_model:
            logger.warning("ML model not available; falling back to rule-based")
            return None

        try:

            input_text = f"translate English to sign gloss: {text}"
            inputs = self.t5_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)

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
                "confidence": 0.75,  
                "method": "ml-based",
            }
        except Exception as e:
            logger.error(f"ML gloss generation failed: {e}")
            return None

    def generate(self, reordered_data: Dict[str, Any]) -> Dict[str, Any]:

        return self.generate_rule_based(reordered_data)

_generator = GlossGenerator(use_ml_model=False)  

def generate_gloss(reordered_data: Dict[str, Any]) -> Dict[str, Any]:

    return _generator.generate(reordered_data)

gloss_generator = GlossGenerator()
