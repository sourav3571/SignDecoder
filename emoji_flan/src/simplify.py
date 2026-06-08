import os
import string
from typing import List
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_distances

# Load a pretrained sentence transformer (download once)
_ST_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# Simple vocabulary file (one word per line)
_SIMPLE_VOCAB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'simple_vocab.txt')

def _load_simple_vocab() -> List[str]:
    if not os.path.exists(_SIMPLE_VOCAB_PATH):
        raise FileNotFoundError(f"Simple vocabulary file not found at {_SIMPLE_VOCAB_PATH}")
    with open(_SIMPLE_VOCAB_PATH, 'r', encoding='utf-8') as f:
        vocab = [line.strip() for line in f if line.strip()]
    return vocab

_SIMPLE_VOCAB = _load_simple_vocab()
# Pre‑compute embeddings for the simple vocab – shape (N, D)
_SIMPLE_EMBS = torch.tensor(_ST_MODEL.encode(_SIMPLE_VOCAB, convert_to_tensor=True))
# Normalise for cosine similarity
_SIMPLE_EMBS = torch.nn.functional.normalize(_SIMPLE_EMBS, p=2, dim=1)

# Very small stop‑word list – can be expanded later
_STOPWORDS = {
    'the', 'a', 'an', 'is', 'was', 'were', 'am', 'are', 'be', 'been', 'being',
    'and', 'or', 'but', 'if', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
    'to', 'in', 'on', 'as', 'that', 'this', 'these', 'those', 'it', 'its', 'he',
    'she', 'they', 'them', 'his', 'her', 'their', 'my', 'your', 'our'
}

def _clean_word(word: str) -> str:
    """Lower‑case and strip punctuation from a token."""
    return word.lower().strip(string.punctuation)

def simplify_sentence(sentence: str, top_k: int = 5, similarity_threshold: float = 0.65) -> str:
    """Simplify a sentence by replacing each content word with the nearest simple vocab word.

    Args:
        sentence: Raw input sentence.
        top_k: Number of nearest neighbours to consider (default 5).
        similarity_threshold: Minimum cosine similarity required to accept a replacement.

    Returns:
        A simplified sentence (string) with stopwords removed.
    """
    # Tokenise naively – split on whitespace
    tokens = sentence.split()
    simplified_tokens = []
    for token in tokens:
        clean = _clean_word(token)
        if not clean or clean in _STOPWORDS:
            continue  # drop stopwords
        # Encode the word
        emb = torch.tensor(_ST_MODEL.encode([clean], convert_to_tensor=True))
        emb = torch.nn.functional.normalize(emb, p=2, dim=1)  # (1, D)
        # Cosine similarity with simple vocab (torch does dot product for normalized vectors)
        sims = torch.matmul(emb, _SIMPLE_EMBS.t()).squeeze(0)  # (N,)
        # Get top‑k indices
        top_vals, top_idx = torch.topk(sims, k=top_k)
        # Choose the best that exceeds the threshold
        best_idx = None
        for val, idx in zip(top_vals.tolist(), top_idx.tolist()):
            if val >= similarity_threshold:
                best_idx = idx
                break
        if best_idx is not None:
            replacement = _SIMPLE_VOCAB[best_idx]
            simplified_tokens.append(replacement)
        else:
            # If nothing passes the threshold, keep the original (lower‑cased) word
            simplified_tokens.append(clean)
    return " ".join(simplified_tokens)
