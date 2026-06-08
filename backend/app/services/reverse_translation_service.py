import os
import json
import logging

logger = logging.getLogger(__name__)

# Categorized dictionary for reconstruction
SUBJECTS = {"I", "YOU", "HE", "SHE", "WE", "THEY", "MY", "YOUR", "ME", "US", "THEM", "SOURAV", "PRIYA", "AMIT", "MOTHER", "FATHER", "BROTHER", "SISTER", "FAMILY"}
VERBS = {"EAT", "GO", "RUN", "PLAY", "COOK", "DRINK", "SLEEP", "WALK", "DRIVE", "GIVE", "WANT", "LIKE", "LOVE", "TAKE"}
LOCATIONS = {"HOME", "SCHOOL", "OFFICE", "HOSPITAL", "BANK", "STORE", "PARK"}
TIMES = {"YESTERDAY", "TODAY", "TOMORROW", "MORNING", "NIGHT", "AFTERNOON", "EVENING"}
NEGATIONS = {"NOT", "NEVER", "NO", "NOT-LIKE"}

# Categorized dictionary for reconstruction
SUBJECTS = {"I", "YOU", "HE", "SHE", "WE", "THEY", "MY", "YOUR", "ME", "US", "THEM", "SOURAV", "PRIYA", "AMIT", "MOTHER", "FATHER", "BROTHER", "SISTER", "FAMILY", "SELF", "PERSON"}
VERBS = {"EAT", "GO", "RUN", "PLAY", "COOK", "DRINK", "SLEEP", "WALK", "DRIVE", "GIVE", "WANT", "LIKE", "LOVE", "TAKE", "SEE", "KNOW"}
LOCATIONS = {"HOME", "SCHOOL", "OFFICE", "HOSPITAL", "BANK", "STORE", "PARK", "HOUSE", "BUILDING", "PLACE", "MIX"}
TIMES = {"YESTERDAY", "TODAY", "TOMORROW", "MORNING", "NIGHT", "AFTERNOON", "EVENING", "SUN", "DAY"}
NEGATIONS = {"NOT", "NEVER", "NO", "NOT-LIKE", "BROKEN", "WRONG"}

# Critical overrides: emojis where we ALWAYS want a specific gloss regardless
# of what the auto-generated dictionary says (grammar-critical mappings)
CRITICAL_OVERRIDES = {
    "👤": "I",        "👉": "HIM",       "😊": "HAPPY",    "😄": "HAPPY",
    "😔": "SAD",      "✅": "YES",        "❌": "NO",        "🤔": "QUESTION",
    "👍": "LIKE",     "👎": "NOT-LIKE",  "🏃": "GO",        "❤️": "LOVE",
    "🙏": "PLEASE",   "🥺": "PLEADING",  "🏠": "HOME",      "🏫": "SCHOOL",
    "🏥": "HOSPITAL", "📱": "PHONE",     "📚": "BOOK",      "💻": "COMPUTER",
    "🚗": "CAR",      "🏢": "OFFICE",    "🥛": "MILK",
    "👨‍👩‍👧‍👦": "FAMILY", "👋": "HELLO",
}

# Core mapping tables — populated at module load time
EMOJI_TO_GLOSS: dict = {}
GLOSS_TO_EMOJI: dict = {}

def _load_dictionaries():
    """Load both directions from the generated emoji_to_label.json and label_to_emoji.json."""
    _HERE = os.path.dirname(os.path.abspath(__file__))
    _MODELS = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "models", "emoji_ml")

    # ── Forward: label → emoji (for building GLOSS_TO_EMOJI) ──────────────────
    fwd_path = os.path.join(_MODELS, "label_to_emoji.json")
    if os.path.exists(fwd_path):
        with open(fwd_path, "r", encoding="utf-8") as f:
            label_to_emoji = json.load(f)
        for label, emoji in label_to_emoji.items():
            clean_gloss = label.upper()
            GLOSS_TO_EMOJI[clean_gloss] = emoji
        logger.info(f"ReverseService: loaded {len(GLOSS_TO_EMOJI)} GLOSS→EMOJI entries")

    # ── Reverse: emoji → label (data-driven, 1120 unique emojis) ──────────────
    rev_path = os.path.join(_MODELS, "emoji_to_label.json")
    if os.path.exists(rev_path):
        with open(rev_path, "r", encoding="utf-8") as f:
            emoji_to_label = json.load(f)
        for emoji, label in emoji_to_label.items():
            # Convert label to GLOSS style (uppercase, underscores preserved for lookup)
            gloss = label.upper().replace(" ", "_")
            EMOJI_TO_GLOSS[emoji] = gloss
        logger.info(f"ReverseService: loaded {len(EMOJI_TO_GLOSS)} EMOJI→GLOSS entries from emoji_to_label.json")
    else:
        logger.warning("emoji_to_label.json not found — reverse service will have limited coverage")

    # ── Apply critical overrides last (highest priority) ──────────────────────
    EMOJI_TO_GLOSS.update(CRITICAL_OVERRIDES)
    logger.info(f"ReverseService: applied {len(CRITICAL_OVERRIDES)} critical overrides")

try:
    _load_dictionaries()
except Exception as e:
    logger.error(f"ReverseTranslationService dictionary load failed: {e}")


# ── Comprehensive Verb Conjugation Table ──────────────────────────────────────
# Format: (GLOSS, tense) -> conjugated form
VERB_CONJUGATIONS: dict[tuple, str] = {
    # Irregular verbs
    ("EAT",    "past"): "ate",         ("EAT",    "present"): "eat",       ("EAT",    "future"): "will eat",
    ("GO",     "past"): "went",        ("GO",     "present"): "go",        ("GO",     "future"): "will go",
    ("RUN",    "past"): "ran",         ("RUN",    "present"): "run",       ("RUN",    "future"): "will run",
    ("DRIVE",  "past"): "drove",       ("DRIVE",  "present"): "drive",     ("DRIVE",  "future"): "will drive",
    ("GIVE",   "past"): "gave",        ("GIVE",   "present"): "give",      ("GIVE",   "future"): "will give",
    ("TAKE",   "past"): "took",        ("TAKE",   "present"): "take",      ("TAKE",   "future"): "will take",
    ("DRINK",  "past"): "drank",       ("DRINK",  "present"): "drink",     ("DRINK",  "future"): "will drink",
    ("COME",   "past"): "came",        ("COME",   "present"): "come",      ("COME",   "future"): "will come",
    ("KNOW",   "past"): "knew",        ("KNOW",   "present"): "know",      ("KNOW",   "future"): "will know",
    ("SEE",    "past"): "saw",         ("SEE",    "present"): "see",       ("SEE",    "future"): "will see",
    ("MEET",   "past"): "met",         ("MEET",   "present"): "meet",      ("MEET",   "future"): "will meet",
    ("BUY",    "past"): "bought",      ("BUY",    "present"): "buy",       ("BUY",    "future"): "will buy",
    ("SEND",   "past"): "sent",        ("SEND",   "present"): "send",      ("SEND",   "future"): "will send",
    ("TEACH",  "past"): "taught",      ("TEACH",  "present"): "teach",     ("TEACH",  "future"): "will teach",
    ("WRITE",  "past"): "wrote",       ("WRITE",  "present"): "write",     ("WRITE",  "future"): "will write",
    ("READ",   "past"): "read",        ("READ",   "present"): "read",      ("READ",   "future"): "will read",
    ("THINK",  "past"): "thought",     ("THINK",  "present"): "think",     ("THINK",  "future"): "will think",
    ("FEEL",   "past"): "felt",        ("FEEL",   "present"): "feel",      ("FEEL",   "future"): "will feel",
    ("TELL",   "past"): "told",        ("TELL",   "present"): "tell",      ("TELL",   "future"): "will tell",
    ("MAKE",   "past"): "made",        ("MAKE",   "present"): "make",      ("MAKE",   "future"): "will make",
    ("FIND",   "past"): "found",       ("FIND",   "present"): "find",      ("FIND",   "future"): "will find",
    # Regular verbs (past = base + ed)
    ("PLAY",   "past"): "played",      ("PLAY",   "present"): "play",      ("PLAY",   "future"): "will play",
    ("COOK",   "past"): "cooked",      ("COOK",   "present"): "cook",      ("COOK",   "future"): "will cook",
    ("WALK",   "past"): "walked",      ("WALK",   "present"): "walk",      ("WALK",   "future"): "will walk",
    ("TALK",   "past"): "talked",      ("TALK",   "present"): "talk",      ("TALK",   "future"): "will talk",
    ("HELP",   "past"): "helped",      ("HELP",   "present"): "help",      ("HELP",   "future"): "will help",
    ("LIKE",   "past"): "liked",       ("LIKE",   "present"): "like",      ("LIKE",   "future"): "will like",
    ("LOVE",   "past"): "loved",       ("LOVE",   "present"): "love",      ("LOVE",   "future"): "will love",
    ("CALL",   "past"): "called",      ("CALL",   "present"): "call",      ("CALL",   "future"): "will call",
    ("OPEN",   "past"): "opened",      ("OPEN",   "present"): "open",      ("OPEN",   "future"): "will open",
    ("LEARN",  "past"): "learned",     ("LEARN",  "present"): "learn",     ("LEARN",  "future"): "will learn",
    ("WANT",   "past"): "wanted",      ("WANT",   "present"): "want",      ("WANT",   "future"): "will want",
    ("WORK",   "past"): "worked",      ("WORK",   "present"): "work",      ("WORK",   "future"): "will work",
    ("STUDY",  "past"): "studied",     ("STUDY",  "present"): "study",     ("STUDY",  "future"): "will study",
    ("SLEEP",  "past"): "slept",       ("SLEEP",  "present"): "sleep",     ("SLEEP",  "future"): "will sleep",
    ("WAIT",   "past"): "waited",      ("WAIT",   "present"): "wait",      ("WAIT",   "future"): "will wait",
    ("ASK",    "past"): "asked",       ("ASK",    "present"): "ask",       ("ASK",    "future"): "will ask",
    ("SHOW",   "past"): "showed",      ("SHOW",   "present"): "show",      ("SHOW",   "future"): "will show",
    ("TRY",    "past"): "tried",       ("TRY",    "present"): "try",       ("TRY",    "future"): "will try",
    ("USE",    "past"): "used",        ("USE",    "present"): "use",       ("USE",    "future"): "will use",
    ("VISIT",  "past"): "visited",     ("VISIT",  "present"): "visit",     ("VISIT",  "future"): "will visit",
}

# ── Concept-to-Verb inference ──────────────────────────────────────────────────
# When no verb gloss is found, we infer a sensible verb from object/concept glosses.
# Maps gloss keyword -> (verb_present, verb_past, verb_future)
CONCEPT_TO_VERB: dict[str, tuple] = {
    # Food / eating
    "FOOD": ("eat", "ate", "will eat"),
    "PIZZA": ("eat", "ate", "will eat"),
    "BURGER": ("eat", "ate", "will eat"),
    "RICE": ("eat", "ate", "will eat"),
    "MEAL": ("eat", "ate", "will eat"),
    "BREAD": ("eat", "ate", "will eat"),
    "FRUIT": ("eat", "ate", "will eat"),
    "WATER": ("drink", "drank", "will drink"),
    "MILK": ("drink", "drank", "will drink"),
    "JUICE": ("drink", "drank", "will drink"),
    "TEA": ("drink", "drank", "will drink"),
    # Education
    "SCHOOL": ("study", "studied", "will study"),
    "BOOK": ("read", "read", "will read"),
    "EXAM": ("take an exam", "took an exam", "will take an exam"),
    "STUDY": ("study", "studied", "will study"),
    "LEARN": ("learn", "learned", "will learn"),
    # Emotions / states
    "HAPPY": ("feel happy", "felt happy", "will feel happy"),
    "SAD": ("feel sad", "felt sad", "will feel sad"),
    "ANGRY": ("feel angry", "felt angry", "will feel angry"),
    "LOVE": ("feel love", "felt love", "will feel love"),
    "FEAR": ("feel afraid", "felt afraid", "will feel afraid"),
    "PAIN": ("feel pain", "felt pain", "will feel pain"),
    # Places / movement
    "HOME": ("go home", "went home", "will go home"),
    "HOSPITAL": ("go to the hospital", "went to the hospital", "will go to the hospital"),
    "OFFICE": ("go to the office", "went to the office", "will go to the office"),
    "MARKET": ("go to the market", "went to the market", "will go to the market"),
    "PARK": ("go to the park", "went to the park", "will go to the park"),
    # Communication
    "PHONE": ("call", "called", "will call"),
    "MESSAGE": ("send a message", "sent a message", "will send a message"),
    # Other
    "MONEY": ("need money", "needed money", "will need money"),
    "MEDICINE": ("take medicine", "took medicine", "will take medicine"),
    "HELP": ("need help", "needed help", "will need help"),
}

# ── Location → preposition mapping ────────────────────────────────────────────
LOCATION_PREPS: dict[str, str] = {
    "HOME":     "home",          # "go home" not "go to home"
    "HOUSE":    "home",
    "SCHOOL":   "to school",
    "OFFICE":   "to the office",
    "HOSPITAL": "to the hospital",
    "BANK":     "to the bank",
    "STORE":    "to the store",
    "MARKET":   "to the market",
    "PARK":     "to the park",
    "BUILDING": "to the building",
    "PLACE":    "to the place",
    "MIX":      "there",
}

# ── Time → English adverb ──────────────────────────────────────────────────────
TIME_WORDS: dict[str, str] = {
    "YESTERDAY": "yesterday",
    "TODAY": "today",
    "TOMORROW": "tomorrow",
    "MORNING": "in the morning",
    "AFTERNOON": "in the afternoon",
    "EVENING": "in the evening",
    "NIGHT": "at night",
    "SUN": "on a sunny day",
    "DAY": "during the day",
}

# ── Emotion glosses that imply a state (not an action) ────────────────────────
EMOTION_GLOSSES = {
    "HAPPY", "SAD", "ANGRY", "FEAR", "SURPRISED", "DISGUST",
    "LOVE", "CALM", "ANXIOUS", "EXCITED", "BORED", "TIRED",
    "COMFORTABLE", "UNCOMFORTABLE", "PAIN", "GRIEF", "JOY",
    "SATISFIED", "DISAPPOINTED", "GRATEFUL", "PROUD", "JEALOUS",
    "LONELY", "CONFUSED", "NERVOUS", "RELAXED", "FRUSTRATED",
}

# ── Pronoun map ────────────────────────────────────────────────────────────────
PRONOUN_MAP: dict[str, str] = {
    "I": "I", "YOU": "you", "HE": "he", "SHE": "she",
    "WE": "we", "THEY": "they", "MY": "my", "YOUR": "your",
    "ME": "me", "US": "us", "THEM": "them", "HIM": "him",
    "SELF": "I", "PERSON": "someone",
    "MOTHER": "my mother", "FATHER": "my father",
    "BROTHER": "my brother", "SISTER": "my sister",
    "FAMILY": "my family", "FRIEND": "my friend",
}

# ── Third-person singular subjects ───────────────────────────────────────────
THIRD_SINGULAR = {"he", "she", "it", "my mother", "my father",
                  "my brother", "my sister", "someone"}


def _conjugate(verb_gloss: str, tense: str, subject: str) -> str:
    """Return the correctly conjugated verb form."""
    key = (verb_gloss.upper(), tense)
    if key in VERB_CONJUGATIONS:
        base = VERB_CONJUGATIONS[key]
        # Add -s for 3rd person singular present
        if tense == "present" and subject in THIRD_SINGULAR:
            if " " not in base:   # only simple verbs (not "will eat")
                if base.endswith(("s", "sh", "ch", "x", "z")):
                    return base + "es"
                elif base.endswith("y") and not base[-2] in "aeiou":
                    return base[:-1] + "ies"
                else:
                    return base + "s"
        return base
    # Fallback: regular verb with -ed / -s
    v = verb_gloss.lower()
    if tense == "past":
        if v.endswith("e"):
            return v + "d"
        elif v.endswith("y") and v[-2] not in "aeiou":
            return v[:-1] + "ied"
        else:
            return v + "ed"
    elif tense == "future":
        return f"will {v}"
    else:
        if subject in THIRD_SINGULAR:
            return v + "s"
        return v


def _negated_verb(verb_gloss: str, tense: str, subject: str) -> str:
    """Build a negated verb phrase: 'do not eat', 'did not go', etc."""
    v = verb_gloss.lower()
    if tense == "past":
        return f"did not {v}"
    elif tense == "future":
        return f"will not {v}"
    else:
        aux = "does not" if subject in THIRD_SINGULAR else "do not"
        return f"{aux} {v}"


def _infer_verb_from_concepts(object_glosses: list, tense: str):
    """Infer a verb phrase from object/concept glosses when no verb emoji is present."""
    for g in object_glosses:
        if g in CONCEPT_TO_VERB:
            pres, past, fut = CONCEPT_TO_VERB[g]
            if tense == "past":
                return past
            elif tense == "future":
                return fut
            else:
                return pres
    return None


class ReverseTranslationService:



    @staticmethod
    def reverse_translate(emoji_sequence_str: str) -> dict:
        """
        Maps emoji sequence → English via:
          1. emoji_to_label.json dictionary (data-driven, 1120 emojis + critical overrides)
          2. Linguistic role classification: Subject / Verb / Object / Location / Time
          3. Concept-to-verb inference when no explicit verb emoji present
          4. Full SVO English reconstruction with tense, negation, question support
        """
        # ── Step 1: Tokenise & Map ─────────────────────────────────────────────
        emoji_tokens = [em.strip() for em in emoji_sequence_str.strip().split() if em.strip()]

        glosses: list[str] = []
        for em in emoji_tokens:
            gloss = EMOJI_TO_GLOSS.get(em)
            if not gloss:
                for key, val in EMOJI_TO_GLOSS.items():
                    if key.strip() in em or em.strip() in key:
                        gloss = val
                        break
            if not gloss:
                clean = em.strip("[]").upper()
                gloss = clean if clean else "UNKNOWN"
            glosses.append(gloss.upper())

        # ── Step 2: Role Classification ────────────────────────────────────────
        subject_list:  list[str] = []
        verb_list:     list[str] = []
        object_list:   list[str] = []
        location_list: list[str] = []
        time_list:     list[str] = []
        emotion_list:  list[str] = []
        is_negated  = False
        is_question = False

        for g in glosses:
            if g in {"UNKNOWN", "CONCEPT"}:
                continue
            if g in NEGATIONS:
                is_negated = True
                if "LIKE" in g:
                    verb_list.append("LIKE")
            elif g in {"QUESTION", "QUESTION_MARK", "QUESTION-MARK", "QUERY"}:
                is_question = True
            elif g in TIMES:
                time_list.append(g)
            elif g in SUBJECTS:
                subject_list.append(g)
            elif g in VERBS:
                verb_list.append(g)
            elif g in LOCATIONS:
                location_list.append(g)
            elif g in EMOTION_GLOSSES:
                emotion_list.append(g)
            else:
                object_list.append(g)

        # ── Step 3: Tense ─────────────────────────────────────────────────────
        tense = "present"
        if any(t in {"YESTERDAY", "MORNING"} for t in time_list):
            tense = "past"
        elif "TOMORROW" in time_list:
            tense = "future"

        # ── Step 4: Subject ───────────────────────────────────────────────────
        subj_gloss = subject_list[0] if subject_list else "I"
        subj = PRONOUN_MAP.get(subj_gloss, subj_gloss.capitalize())

        # ── Step 5: Verb phrase ────────────────────────────────────────────────
        verb_phrase = ""

        if verb_list:
            v_gloss = verb_list[0]
            verb_phrase = _negated_verb(v_gloss, tense, subj) if is_negated else _conjugate(v_gloss, tense, subj)

        elif emotion_list and not object_list and not location_list:
            # Pure emotion: "I 😊" → "I feel happy"
            em_word = emotion_list[0].lower()
            if tense == "past":
                verb_phrase = f"felt {em_word}"
            elif tense == "future":
                verb_phrase = f"will feel {em_word}"
            else:
                aux = "feels" if subj in THIRD_SINGULAR else "feel"
                verb_phrase = f"{aux} {em_word}"

        else:
            # No explicit verb: infer from object/location context
            all_concepts = object_list + location_list + emotion_list
            inferred = _infer_verb_from_concepts(all_concepts, tense)
            if inferred:
                prefix = "did not " if is_negated else ""
                verb_phrase = prefix + inferred
            else:
                # Copula fallback
                if tense == "past":
                    verb_phrase = "was" if (subj == "I" or subj in THIRD_SINGULAR) else "were"
                elif tense == "future":
                    verb_phrase = "will be"
                else:
                    verb_phrase = "am" if subj == "I" else ("is" if subj in THIRD_SINGULAR else "are")

        # ── Step 6: Remaining object words ───────────────────────────────────
        # Drop concepts already baked into the inferred verb phrase
        consumed = {c for c in object_list + location_list if c in CONCEPT_TO_VERB and c.lower() in verb_phrase.lower()}
        remaining_obj = [o.lower().replace("_", " ") for o in object_list if o not in consumed]
        # Append emotions as adjectives when there's an explicit verb
        if verb_list and emotion_list:
            remaining_obj = [e.lower() for e in emotion_list] + remaining_obj
        obj_phrase = " ".join(remaining_obj)

        # ── Step 7: Location phrase ───────────────────────────────────────────
        loc_phrase = ""
        if location_list:
            l_gloss = location_list[0]
            loc_str = LOCATION_PREPS.get(l_gloss, f"to {l_gloss.lower()}")
            if loc_str.lower() not in verb_phrase.lower():
                loc_phrase = loc_str

        # ── Step 8: Time adverb ───────────────────────────────────────────────
        time_phrase = TIME_WORDS.get(time_list[0], time_list[0].lower()) if time_list else ""

        # ── Step 9: Assemble ──────────────────────────────────────────────────
        if is_question:
            v_base = verb_list[0].lower() if verb_list else "be"
            if tense == "past":
                aux = "Did"
            elif tense == "future":
                aux = "Will"
            else:
                aux = "Does" if subj in THIRD_SINGULAR else "Do"
            q_parts = [aux, subj]
            if is_negated:
                q_parts.append("not")
            q_parts.append(v_base)
            if obj_phrase:  q_parts.append(obj_phrase)
            if loc_phrase:  q_parts.append(loc_phrase)
            if time_phrase: q_parts.append(time_phrase)
            sentence = " ".join(q_parts).strip() + "?"
        else:
            parts = [subj, verb_phrase]
            if obj_phrase:  parts.append(obj_phrase)
            if loc_phrase:  parts.append(loc_phrase)
            if time_phrase: parts.append(time_phrase)
            sentence = " ".join(p for p in parts if p).strip() + "."

        sentence = sentence[0].upper() + sentence[1:]
        sentence = " ".join(sentence.split())

        return {
            "emoji_sequence": emoji_sequence_str,
            "glosses":        glosses,
            "reconstructed_text": sentence,
            "confidence_score": 0.95,
        }
