"""
build_reverse_dataset.py
------------------------
Generates two artifacts from the existing label_to_emoji.json:

  1. emoji_to_label.json   — canonical best-label for each unique emoji
  2. reverse_train.json    — FLAN-T5 training pairs for emoji→label task
  3. reverse_val.json      — validation split (10%)

Disambiguation strategy when many labels map to the same emoji:
  Priority 1 — label that appears in CORE_WORDS (clean single-word glosses)
  Priority 2 — label with no underscores (simplest human-readable word)
  Priority 3 — shortest label (most compact concept)
  Priority 4 — alphabetical tiebreak (deterministic)
"""

import os
import json
import random
import re

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE         = os.path.dirname(os.path.abspath(__file__))
_ROOT         = os.path.dirname(os.path.dirname(_HERE))
LABEL_TO_EMOJI = os.path.join(_ROOT, "backend", "models", "emoji_ml", "label_to_emoji.json")
OUT_DICT       = os.path.join(_ROOT, "backend", "models", "emoji_ml", "emoji_to_label.json")
OUT_TRAIN      = os.path.join(_ROOT, "emoji_flan", "data", "reverse_train.json")
OUT_VAL        = os.path.join(_ROOT, "emoji_flan", "data", "reverse_val.json")

# ── Core single-concept words (highest priority in disambiguation) ─────────────
# Emojis used as generic placeholders for 100s of abstract concepts.
# Their canonical label should be a generic fallback, not a random winner.
PLACEHOLDER_EMOJIS = {
    "✨",   # used for 3000+ abstract/unknown concepts
    "🖱️",  # used as generic 'action'
    "👋",  # used as generic 'person'
}

CORE_WORDS = {
    # pronouns / people
    "i", "you", "he", "she", "we", "they", "me", "us", "them",
    "person", "man", "woman", "boy", "girl", "child", "baby",
    "family", "friend", "mother", "father", "brother", "sister",
    # common verbs (base forms)
    "eat", "go", "run", "play", "cook", "drink", "sleep", "walk",
    "drive", "give", "want", "like", "love", "take", "see", "know",
    "read", "write", "work", "study", "help", "ask", "say", "call",
    "buy", "sell", "send", "make", "come", "meet", "learn", "open",
    # common nouns
    "home", "school", "office", "hospital", "bank", "store", "park",
    "food", "water", "book", "phone", "car", "house", "money", "time",
    "day", "night", "morning", "work", "music", "sport", "game",
    # common adjectives / states
    "happy", "sad", "angry", "love", "fear", "good", "bad", "big",
    "small", "hot", "cold", "new", "old", "fast", "slow", "yes", "no",
    # emotions
    "joy", "anger", "fear", "surprise", "disgust", "grief", "calm",
    "anxiety", "celebration", "achievement", "affection",
}


def clean_label_to_text(label: str) -> str:
    """Convert a snake_case label to a readable gloss: 'academic_aid' → 'academic aid'."""
    return label.replace("_", " ").strip()





def score_label(label: str) -> tuple:
    """
    Lower score = higher priority.
    Returns (core_priority, underscore_count, length, label)
    """
    text = label.replace("_", " ").lower()
    is_core = 1 if text not in CORE_WORDS else 0          # 0 = core word wins
    underscore_count = label.count("_")
    return (is_core, underscore_count, len(label), label)


def build_emoji_to_label(label_to_emoji: dict) -> dict:
    """
    Group all labels by their emoji, then pick the single best canonical label.
    For multi-emoji sequences (e.g. '🚜 🌾'), treat the whole sequence as one key.
    """
    """
    Group all labels by their emoji, then pick the single best canonical label.
    For multi-emoji sequences (e.g. '🚜 🌾'), treat the whole sequence as one key.
    Placeholder emojis (✨ etc.) get a generic canonical label 'concept'.
    """
    emoji_candidates: dict[str, list[str]] = {}

    for label, emoji_seq in label_to_emoji.items():
        emoji_seq = emoji_seq.strip()
        if not emoji_seq:
            continue
        emoji_candidates.setdefault(emoji_seq, []).append(label)

    emoji_to_label: dict[str, str] = {}
    for emoji_seq, candidates in emoji_candidates.items():
        # Placeholder emojis: too overloaded to give a meaningful label
        if emoji_seq.strip() in PLACEHOLDER_EMOJIS:
            emoji_to_label[emoji_seq] = "concept"   # generic canonical
            continue
        # Sort by our priority scheme and pick the top one
        best = sorted(candidates, key=score_label)[0]
        emoji_to_label[emoji_seq] = best

    return emoji_to_label


def make_training_pairs(label_to_emoji: dict, emoji_to_label: dict) -> list[dict]:
    """
    Generate FLAN-T5 style training pairs for the reverse task.

    We produce pairs in two ways:
      A) Canonical pair   — one clean pair per unique emoji
      B) Label-side pairs — for labels that map to a multi-emoji sequence,
                            generate a pair where the model must output that
                            specific label given the full emoji sequence.

    Input format : "translate emoji to label: <emoji_sequence>"
    Output format: "<label_text>"   (human-readable, spaces not underscores)
    """
    pairs: list[dict] = []
    seen: set[str] = set()

    # A) One canonical pair per unique emoji
    for emoji_seq, best_label in emoji_to_label.items():
        key = f"{emoji_seq}||{best_label}"
        if key in seen:
            continue
        seen.add(key)
        pairs.append({
            "input":  f"translate emoji to label: {emoji_seq}",
            "output": clean_label_to_text(best_label),
            "type":   "canonical"
        })

    # B) Every label → its emoji sequence (many-to-one on emoji side)
    #    This trains the model to also accept "non-canonical" outputs
    #    and generalises the coverage.
    for label, emoji_seq in label_to_emoji.items():
        emoji_seq = emoji_seq.strip()
        if not emoji_seq:
            continue
        # skip if it's already covered by the canonical pair
        canonical = emoji_to_label.get(emoji_seq, "")
        if label == canonical:
            continue           # already added in step A
        key = f"{emoji_seq}||{label}"
        if key in seen:
            continue
        seen.add(key)
        pairs.append({
            "input":  f"translate emoji to label: {emoji_seq}",
            "output": clean_label_to_text(label),
            "type":   "variant"
        })

    return pairs


def split_and_save(pairs: list[dict], val_ratio: float = 0.10):
    random.seed(42)
    random.shuffle(pairs)
    split = int(len(pairs) * (1 - val_ratio))
    train, val = pairs[:split], pairs[split:]

    with open(OUT_TRAIN, "w", encoding="utf-8") as f:
        json.dump(train, f, ensure_ascii=False, indent=2)
    with open(OUT_VAL, "w", encoding="utf-8") as f:
        json.dump(val, f, ensure_ascii=False, indent=2)

    return train, val


def main():
    print("=" * 60)
    print("  REVERSE DATASET BUILDER")
    print("=" * 60)

    # 1. Load source
    with open(LABEL_TO_EMOJI, "r", encoding="utf-8") as f:
        label_to_emoji = json.load(f)
    print(f"\n[1] Loaded label_to_emoji.json  →  {len(label_to_emoji):,} entries")

    # 2. Build canonical emoji → label map
    emoji_to_label = build_emoji_to_label(label_to_emoji)
    print(f"[2] Unique emoji sequences      →  {len(emoji_to_label):,}")

    # Show disambiguation examples
    print("\n--- Disambiguation Examples (multiple labels → 1 winner) ---")
    shown = 0
    from collections import defaultdict
    grouped: dict[str, list[str]] = defaultdict(list)
    for lbl, em in label_to_emoji.items():
        grouped[em.strip()].append(lbl)

    for em, candidates in grouped.items():
        if len(candidates) > 1:
            winner = emoji_to_label.get(em, "?")
            losers = [c for c in candidates if c != winner][:3]
            print(f"  {em!r:6}  winner='{winner}'  losers={losers}")
            shown += 1
            if shown >= 8:
                break

    # 3. Save emoji_to_label.json
    with open(OUT_DICT, "w", encoding="utf-8") as f:
        json.dump(emoji_to_label, f, ensure_ascii=False, indent=2)
    print(f"\n[3] Saved emoji_to_label.json  →  {OUT_DICT}")

    # 4. Build training pairs
    pairs = make_training_pairs(label_to_emoji, emoji_to_label)
    print(f"[4] Total training pairs        →  {len(pairs):,}")
    canonical = sum(1 for p in pairs if p["type"] == "canonical")
    variant   = sum(1 for p in pairs if p["type"] == "variant")
    print(f"    Canonical pairs             →  {canonical:,}")
    print(f"    Variant pairs               →  {variant:,}")

    # 5. Sample display
    print("\n--- Sample Pairs ---")
    for p in random.sample(pairs, min(8, len(pairs))):
        print(f"  IN : {p['input']}")
        print(f"  OUT: {p['output']}")
        print()

    # 6. Split and save
    train, val = split_and_save(pairs)
    print(f"[5] Train pairs                 →  {len(train):,}  →  {OUT_TRAIN}")
    print(f"    Val   pairs                 →  {len(val):,}   →  {OUT_VAL}")
    print("\n✅  Done! Reverse dataset built successfully.")


if __name__ == "__main__":
    main()
