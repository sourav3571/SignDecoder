# SignDecoder — NLP-Powered Sign Language Translation

> **Turn Words Into Signs. Instantly.**

An accessibility-first, research-grade NLP system that converts typed English into Indian Sign Language (ISL) gloss order with intelligent emoji output. No camera needed. Works on any device.

---

## What Makes SignDecoder Unique?

| Feature | SignDecoder | Typical App |
|---------|-------------|-------------|
| **Technology** | Deep NLP + fine-tuned transformers | Simple emoji replacement |
| **Input Method** | Typed text (works everywhere) | Camera/microphone (privacy concerns) |
| **Output Quality** | Linguistically correct ISL gloss order | Random emoji sequence |
| **Figurative Language** | Detects & simplifies idioms and metaphors | Not supported |
| **Complexity Analysis** | Per-word & sentence-level difficulty scores | No scores |
| **Accessibility** | Built FOR deaf users | Built as an afterthought |

---

## Tech Stack

```
Backend:     FastAPI + Python 3.11 (async, high-performance)
NLP:         spaCy + HuggingFace Transformers (BERT, DeBERTa, RoBERTa, T5)
Simplifier:  10-stage lexical + figurative simplification pipeline
Frontend:    Next.js 14 + TypeScript + Tailwind CSS
Deployment:  Docker + Render + GitHub Actions
```

---

## The Full Pipeline

```
Input: "The physician treated the patient with medication."
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 1 — Preprocessing                                            │
│    • Spell check & contraction expansion                            │
│    • Text normalization                                             │
└──────────────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 2 — Complex Word Identification (CWI)                        │
│    • DeBERTa-v3-base token classifier                               │
│    • Per-word P(complex) score in a single forward pass             │
│    • Focal Loss to handle class imbalance (~30% complex words)      │
│    DATASETS:                                                        │
│      - CWI 2018 Shared Task (~27k annotated tokens)                 │
│      - LexMTurk (~500 sentences)                                    │
│      - BenchLS (~929 sentences)                                     │
└──────────────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 3 — Candidate Generation                                     │
│    • BERT-MLM masked language model to propose substitutes          │
│    • WordNet synset expansion via NLTK                              │
│    • PPDB paraphrase database fallback                              │
│    BASE MODEL: bert-base-uncased (pretrained, HuggingFace)          │
└──────────────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 4 — Figurative Language Detection                            │
│                                                                     │
│  4a. Idiom Classifier                                               │
│      • RoBERTa-base sequence classifier (sentence + phrase)         │
│      DATASETS:                                                      │
│        - MAGPIE Corpus (idiomatic/literal phrase pairs)             │
│        - Synthetic augmentation (200 template sentences)            │
│                                                                     │
│  4b. Metaphor Detector                                              │
│      • RoBERTa-base token classifier                                │
│      DATASETS:                                                      │
│        - VUA Amsterdam Metaphor Corpus (VUAMC)                      │
│        - Synthetic augmentation (200 metaphor sentences)            │
└──────────────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 5 — Figurative Simplification                                │
│    • Idioms → plain English paraphrase via idiom database           │
│    • Metaphors → concrete literal equivalent                        │
│    DATABASE: EPIE Idiom Dataset + curated internal lookup           │
└──────────────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 6 — Word Sense Disambiguation                                │
│    • BERT-base contextual embeddings                                │
│    • WordNet synset selection by cosine similarity                  │
│    BASE MODEL: bert-base-uncased                                    │
└──────────────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 7 — Candidate Ranking (GatedFusionRanker)                    │
│    • 6-feature neural ranker (Linear → ReLU → Sigmoid)             │
│    Features:                                                        │
│      1. MLM probability        (BERT-base-uncased)                  │
│      2. SBERT sentence sim     (all-MiniLM-L6-v2)                  │
│      3. Surprisal reduction    (BERT log-likelihood delta)          │
│      4. Fluency change         (Δ log-likelihood)                   │
│      5. Zipf frequency diff    (wordfreq library)                   │
│      6. GloVe cosine sim       (GloVe 100d)                         │
│    TRAINING: MarginRankingLoss on human preference pairs            │
│    DATASETS: BenchLS + LexMTurk                                     │
└──────────────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 8 — Visual Word Linking                                      │
│    • Emoji mapping via NLTK WordNet + Wikidata lookups              │
│    • Dictionary cache for fast repeat lookups                       │
└──────────────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 9 — ISL Gloss Translation (T5)                               │
│    • T5-small fine-tuned: English → ISL gloss (SOV word order)     │
│    • POS tagging: "Please tag grammatical parts: ..."               │
│    • Translation: "translate english to isl: ..."                  │
│    BASE ARCHITECTURE: T5-small (60M params, Google)                 │
│    TRAINING DATA: PHOENIX-Weather 2014T                             │
│      (German Sign Language gloss corpus, adapted for ISL ordering)  │
└──────────────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────────┐
│  Stage 10 — Emoji Mapping                                           │
│    • Gloss word → emoji via GLOSS_TO_EMOJI dictionary (200+ rules) │
│    • Confidence score per card                                      │
└──────────────────────────────────────────────────────────────────────┘
         ↓
Output: "DOCTOR TREAT PATIENT MEDICINE"  →  👨‍⚕️ 🤲 🧑 💊
```

---

## Model Registry & Training Datasets

| Model File | Architecture | Task | Training Dataset |
|---|---|---|---|
| `cwi_deberta.pt` | DeBERTa-v3-base + Linear head | Complex Word Identification | **CWI 2018 Shared Task** (~27k tokens) + **LexMTurk** + **BenchLS** |
| `gated_fusion_ranker_6f.pt` | 6-feat Linear→ReLU→Sigmoid | Substitute ranking | **BenchLS** + **LexMTurk** (MarginRankingLoss on human preference pairs) |
| `best_model.pt` | BERT-base + custom scorer | Candidate scoring | **BenchLS** + **LexMTurk** |
| `idiom_classifier.pt` | RoBERTa-base + seq classifier | Idiom detection | **MAGPIE Corpus** + **Synthetic** (200 template sentences) |
| `metaphor_detector.pt` | RoBERTa-base + token classifier | Metaphor detection | **VUAMC** (VU Amsterdam Metaphor Corpus) + **Synthetic** |
| `cwi_bert_figurative_v2.pt` | BERT-base + custom head | Figurative CWI | **MAGPIE** + **VUAMC** combined |
| `sentence_to_gloss/model.safetensors` | T5-small (60M params) | English → ISL Gloss | **PHOENIX-Weather 2014T** (adapted for ISL) |

---

## Dataset Details

### CWI 2018 Shared Task
- **Source:** [zenodo.org/record/1172640](https://zenodo.org/record/1172640) / HuggingFace `AyoubChLin/CWI_korpus`
- **Size:** ~27,000 annotated word tokens
- **Domains:** Wikipedia, WikiNews, News
- **Label:** Binary — `1 = complex`, `0 = simple` (majority vote of annotators)

### BenchLS
- **Source:** [github.com/ghpaetzold/benchLS](https://github.com/ghpaetzold/benchLS)
- **Size:** ~929 sentences with ranked substitution candidates
- **Format:** `sentence TAB target_word TAB rank:substitute ...`

### LexMTurk
- **Source:** MTurk crowdsourced lexical simplification benchmark
- **Size:** ~500 sentences with candidate substitutions and human vote counts

### MAGPIE Idiom Corpus
- **Source:** [github.com/hslh/magpie-corpus](https://github.com/hslh/magpie-corpus)
- **Size:** ~56,000 idiom usage examples
- **Label:** `literal` / `idiomatic` per phrase occurrence

### VU Amsterdam Metaphor Corpus (VUAMC)
- **Source:** [ETS Metaphor Research](https://github.com/EducationalTestingService/metaphor)
- **Size:** ~17,000 token-level metaphor annotations
- **Domains:** Academic, conversation, fiction, news
- **Label:** Per-token binary — `1 = metaphorical`, `0 = literal`

### PHOENIX-Weather 2014T
- **Source:** [RWTH Aachen PHOENIX Dataset](https://www-i6.informatik.rwth-aachen.de/~koller/RWTH-PHOENIX/)
- **Size:** ~8,000 sentence pairs (text → DGS gloss)
- **Note:** Originally German Sign Language; adapted here for ISL SOV word-order reordering

---

## Quick Start

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
# → API at http://localhost:8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# → UI at http://localhost:3000
```

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/translate` | POST | Main translation endpoint |
| `/api/convert-to-emoji` | POST | Gloss → emoji conversion |
| `/api/emoji-model-status` | GET | Check emoji model load status |
| `/health` | GET | Backend health check |
| `/docs` | GET | Swagger UI (auto-generated) |
