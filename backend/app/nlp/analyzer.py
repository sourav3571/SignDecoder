
try:
    import spacy
except Exception as spacy_import_error:
    spacy = None

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SemanticAnalyzer:

    def __init__(self, model_name: str = "en_core_web_trf"):

        self.model_name = model_name
        self.nlp: Optional["spacy.Language"] = None
        self._load_model()

    def _load_model(self):

        if spacy is None:
            logger.warning(
                "spaCy import failed. Fallback semantic analyzer will be used instead."
            )
            self.nlp = None
            return

        try:

            try:
                self.nlp = spacy.load(self.model_name)
                logger.info(f"✓ Loaded spaCy model: {self.model_name}")
            except OSError:

                logger.warning(
                    f"Model '{self.model_name}' not found. Using fallback 'en_core_web_sm'.\n"
                    f"For production, install: python -m spacy download en_core_web_trf"
                )
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("✓ Loaded spaCy model: en_core_web_sm (fallback)")
        except Exception as e:
            logger.error(f"✗ Failed to load spaCy model: {e}")
            self.nlp = None

    def _extract_semantic_roles(self, doc) -> Dict[str, List[str]]:

        roles = {
            "subject": [],
            "verb": [],
            "object": [],
            "indirect_object": [],
            "modifier": [],
            "time": [],
            "location": [],
            "negation": [],
            "auxiliary": [],  
        }

        for token in doc:

            if "subj" in token.dep_:
                roles["subject"].append(token.lemma_)

            if token.dep_ == "ROOT" or token.pos_ == "VERB":
                roles["verb"].append(token.lemma_)

            if "obj" in token.dep_:
                roles["object"].append(token.lemma_)

            if token.dep_ == "iobj":
                roles["indirect_object"].append(token.lemma_)

            if token.dep_ == "neg":
                roles["negation"].append(token.text.lower())

            if token.dep_ in ["amod", "advmod"]:
                roles["modifier"].append(token.lemma_)

            if token.pos_ == "AUX":
                roles["auxiliary"].append(token.lemma_)

        for ent in doc.ents:
            if ent.label_ in ["TIME", "DATE", "ORDINAL"]:
                roles["time"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC", "FAC"]:

                roles["location"].append(ent.text)

        time_keywords = {
            "yesterday", "today", "tomorrow", "now", "later", "soon",
            "morning", "afternoon", "evening", "night", "noon", "midnight",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december",
        }

        location_keywords = {
            "home", "work", "school", "office", "hospital", "park",
            "beach", "mountain", "restaurant", "store", "library",
            "here", "there", "where",
        }

        for token in doc:
            if token.text.lower() in time_keywords and token.text not in roles["time"]:
                roles["time"].append(token.text)

            if token.text.lower() in location_keywords and token.text not in roles["location"]:
                roles["location"].append(token.text)

        for key in roles:
            roles[key] = list(set(roles[key]))  

        return roles

    def _detect_tense(self, doc) -> str:

        past_indicators = {"was", "were", "had", "did", "ed"}
        future_indicators = {"will", "shall", "going to"}
        conditional_indicators = {"would", "could", "might", "should"}
        present_indicators = {"is", "am", "are", "do", "does"}

        verb_text = " ".join([token.text.lower() for token in doc if token.pos_ == "VERB" or token.pos_ == "AUX"])

        if any(indicator in verb_text for indicator in future_indicators):
            return "future"
        elif any(indicator in verb_text for indicator in conditional_indicators):
            return "conditional"
        elif any(indicator in verb_text for indicator in past_indicators):
            return "past"
        elif any(indicator in verb_text for indicator in present_indicators):
            return "present"
        else:
            return "unknown"

    def _detect_aspect(self, doc) -> str:

        text_lower = " ".join([token.lemma_.lower() for token in doc])

        if any(aux in text_lower for aux in ["be", "is", "am", "are", "was", "were"]):

            for token in doc:
                if token.tag_ == "VBG":  
                    return "progressive"

        if any(aux in text_lower for aux in ["have", "has", "had"]):
            return "perfective"

        return "habitual"

    def _fallback_analyze(self, text: str) -> Dict[str, Any]:

        words = [w.strip(".,!?;:") for w in text.lower().split() if w.strip()]
        neg_words = {"not", "no", "never", "none", "n't"}
        time_words = {
            "yesterday", "today", "tomorrow", "morning", "afternoon",
            "evening", "night", "now", "later", "soon",
        }
        pronouns = {"i", "you", "he", "she", "we", "they", "it"}
        roles = {"subject": [], "verb": [], "object": [], "time": [], "location": [], "negation": [], "auxiliary": [], "modifier": []}

        for w in words:
            clean_w = w.strip(".,!?;:")
            if clean_w in neg_words:
                roles["negation"].append(clean_w)
            elif clean_w in time_words:
                roles["time"].append(clean_w)
            elif clean_w in pronouns:
                roles["subject"].append(clean_w)
            elif clean_w.endswith("ing"):
                if clean_w not in roles["verb"]:
                    roles["verb"].append(clean_w)
            elif clean_w.endswith("ed"):
                if clean_w not in roles["verb"]:
                    roles["verb"].append(clean_w)
            elif clean_w in {"home", "work", "office", "park", "school", "store"}:
                roles["location"].append(clean_w)
            else:
                if clean_w not in roles["object"]:
                    roles["object"].append(clean_w)

        return {
            "original_text": text,
            "tokens": [{"text": w, "lemma": w, "pos": "NOUN", "tag": "NN", "dep": "obj", "head": w} for w in words],
            "entities": [],
            "semantic_roles": roles,
            "is_question": text.strip().endswith("?"),
            "tense": "unknown",
            "aspect": "unknown",
            "has_negation": len(roles["negation"]) > 0,
            "model_used": "fallback",
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def analyze(self, text: str) -> Dict[str, Any]:

        if not self.nlp:
            return self._fallback_analyze(text)

        doc = self.nlp(text)

        tokens = []
        for token in doc:
            tokens.append({
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,  
                "tag": token.tag_,  
                "dep": token.dep_,  
                "head": token.head.text,  
                "is_stop": token.is_stop,  
            })

        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            })

        semantic_roles = self._extract_semantic_roles(doc)

        is_question = text.rstrip().endswith("?") or any(
            token.tag_ in ["WDT", "WP", "WP$", "WRB"] for token in doc
        )

        tense = self._detect_tense(doc)
        aspect = self._detect_aspect(doc)
        has_negation = len(semantic_roles["negation"]) > 0

        return {
            "original_text": text,
            "tokens": tokens,
            "entities": entities,
            "semantic_roles": semantic_roles,
            "is_question": is_question,
            "tense": tense,
            "aspect": aspect,
            "has_negation": has_negation,
            "model_used": self.model_name,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

_analyzer: Optional[SemanticAnalyzer] = None

def get_analyzer() -> SemanticAnalyzer:

    global _analyzer
    if _analyzer is None:
        _analyzer = SemanticAnalyzer(model_name="en_core_web_trf")
    return _analyzer

def analyze_text(text: str) -> Dict[str, Any]:

    analyzer = get_analyzer()
    return analyzer.analyze(text)

analyzer = SemanticAnalyzer()
