
from typing import Literal

SUPPORTED_SIGN_LANGUAGES = ["ISL"]
CURRENT_SIGN_LANGUAGE: Literal["ISL"] = "ISL"

ISL_CONFIG = {
    "name": "Indian Sign Language",
    "code": "ISL",
    "description": "Sign language used by deaf communities in India",
    "regions": ["India", "Parts of South Asia"],
    "speakers": "2+ million",

    "grammar": {
        "word_order": "Topic-Comment",
        "topic_position": "initial",
        "time_marking": "optional_first_or_last",
        "location_marking": "spatial_setup",
        "verb_agreement": "spatial",
        "uses_classifiers": True,
        "spatial_verbs": True,
        "incorporation": True,  
    },

    "linguistic_features": {
        "classifier_system": True,
        "directional_verbs": True,
        "facial_expressions": "critical",
        "role_shift": True,
        "reduplication": True,
        "spatial_modulation": True,
        "handshape_inventory": 40,  
        "hand_positions": ["neutral_space", "head", "chest", "arm"],
        "movements": ["straight", "curved", "circular", "twisting"],
    },

    "phonology": {
        "handshapes": "iconic",
        "palm_orientation": "distinctive",
        "location": "distinctive",
        "movement": "distinctive",
        "non_manual_markers": ["brow_raise", "head_tilt", "mouth_shape"],
    },

    "morphosyntax": {
        "tense_marking": "optional",
        "aspect_marking": "habitual_perfective",
        "agreement_pattern": "spatial_loci",
        "verb_incorporation": True,
        "noun_verb_distinction": False,  
    },

    "dictionary": {
        "size": "500+ core glosses",
        "sources": ["Indian Deaf Society", "Academic research"],
        "emoji_mappings": True,
        "includes_classifiers": True,
        "includes_facial_markers": True,
    }
}

ISL_PIPELINE_CONFIG = {
    "preprocessing": {
        "enabled": True,
        "spell_check": True,
        "contraction_expansion": True,
        "normalization": True,
    },
    "nlp_analysis": {
        "use_spacy": True,
        "spacy_model": "en_core_web_sm",
        "extract_semantic_roles": True,
        "detect_questions": True,
        "detect_negation": True,
    },
    "reordering": {
        "reorderer_class": "ISLReorderer",
        "module": "app.nlp.isl_reorderer",
        "apply_isl_rules": True,
        "extract_time_marking": True,
        "extract_spatial_setup": True,
    },
    "gloss_generation": {
        "enabled": True,
        "include_classifiers": True,
        "include_facial_markers": True,
    },
    "emoji_mapping": {
        "mapper_class": "ISLEmojiMapper",
        "module": "app.nlp.isl_emoji_mapper",
        "use_isl_dictionary": True,
        "confidence_threshold": 0.3,
        "include_alternatives": True,
    },
    "output": {
        "include_gloss_string": True,
        "include_emoji_sequence": True,
        "include_confidence_scores": True,
        "include_isl_metadata": True,
        "include_spatial_info": True,
        "include_facial_expressions": True,
    }
}

ISL_EMOJI_CONFIG = {
    "strategy": "exact_match_with_fallback",
    "strategies": [
        "exact_match",        
        "semantic_search",    
        "fuzzy_match",        
        "fallback",          
    ],
    "include_alternatives": True,
    "include_lottie_files": True,
    "confidence_weighting": {
        "exact_match": 1.0,
        "semantic_search": 0.8,
        "fuzzy_match": 0.6,
        "fallback": 0.3,
    },
}

ISL_GLOSS_STANDARDS = {
    "format": "all_caps",  
    "separators": " ",     
    "direction_markers": {
        "toward_self": "→1",
        "toward_addressee": "→2",
        "from_right_to_left": "3→1",
    },
    "repetition_marker": "^",  
    "classifier_notation": "CL-",  
    "facial_markers": {
        "question": "QUESTION?",
        "negation": "NOT",
        "emphasis": "!",
    },
    "spatial_loci": {
        "center": "center",
        "right": "right-locus",
        "left": "left-locus",
        "proximal": "here",
        "distal": "there",
    }
}

def get_isl_config() -> dict:

    return {
        "sign_language": ISL_CONFIG,
        "pipeline": ISL_PIPELINE_CONFIG,
        "emoji_mapping": ISL_EMOJI_CONFIG,
        "gloss_standards": ISL_GLOSS_STANDARDS,
        "current_language": CURRENT_SIGN_LANGUAGE,
    }

def get_sign_language_reorderer(sign_language: str = CURRENT_SIGN_LANGUAGE):

    if sign_language == "ISL":
        from app.nlp.isl_reorderer import isl_reorderer
        return isl_reorderer
    elif sign_language == "ASL":

        from app.nlp.reorderer import SignLanguageReorderer
        return SignLanguageReorderer(sign_language="ASL")
    else:
        raise ValueError(f"Unsupported sign language: {sign_language}")

def get_emoji_mapper(sign_language: str = CURRENT_SIGN_LANGUAGE):

    if sign_language == "ISL":
        from app.nlp.isl_emoji_mapper import isl_emoji_mapper
        return isl_emoji_mapper
    elif sign_language == "ASL":

        from app.nlp.emoji_mapper import emoji_mapper
        return emoji_mapper
    else:
        raise ValueError(f"Unsupported sign language: {sign_language}")
