# SignSpeak - NLP-Powered Sign Language Translation

> **Turn Words Into Signs. Instantly.**

An accessibility-first, research-grade NLP system that converts typed English into sign language order with intelligent emoji and animation output. No camera needed. Works on any device.

## What Makes SignSpeak Unique?

| Feature | SignSpeak | Typical App |
|---------|-----------|-------------|
| **Technology** | Deep NLP semantic understanding | Simple emoji replacement |
| **Input Method** | Typed text (works everywhere) | Camera/microphone (privacy concerns) |
| **Output Quality** | Linguistically correct sign order | Random emoji sequence |
| **Confidence Scores** | Every emoji has confidence % | No confidence data |
| **Offline Mode** | Cached results work offline | Must be online |
| **Accessibility** | Built FOR deaf users | Built AS an afterthought |

## Tech Stack

```
Backend:     FastAPI + Python 3.11 (async, high-performance)
NLP:         spaCy + Transformers (semantic understanding)
Cache:       Redis + Celery (fast responses, async tasks)
Database:    PostgreSQL + MongoDB + Pinecone (data, documents, vectors)
Frontend:    Next.js 14 + TypeScript + Tailwind CSS
Deployment:  Docker + AWS/Render + GitHub Actions
```

## The Pipeline

```
"I ate pizza at home yesterday"
         ↓
[Preprocessing]
     • Spell check
     • Expand contractions
     • Normalize text
         ↓
[NLP Analysis]
     WHO: I (PERSON)
     DOING: eat (VERB)
     WHAT: pizza (FOOD)
     WHERE: home (LOCATION)
     WHEN: yesterday (TIME)
         ↓
[Sign Language Reordering]
     English (SVO): I + eat + pizza
     Sign (SOV):    YESTERDAY HOME I PIZZA EAT
         ↓
[Emoji Mapping]
     WITH confidence scores
     YESTERDAY→⬅️📅 (0.95)
     HOME→🏠 (1.00)
     I→👤 (0.75)
     PIZZA→🍕 (1.00)
     EAT→🍽️ (1.00)
         ↓
[Lottie Animation]
     Play sequentially with timing
         ↓
Output: ⬅️📅 🏠 👤 🍕 🍽️
```

## Quick Start (Docker)

```bash
# 1. Clone repo
git clone https://github.com/yourrepo/signspeak.git
cd signspeak

# 2. Setup environment
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Verify health
curl http://localhost:8000/health

# 5. Open API docs
# → http://localhost:8000/docs
```

## Quick Start (Local Development)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
# → API at http://localhost:8000

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
# → UI at http://localhost:3000

# Run the backend
uvicorn app.main:app --reload --reload-dir app --reload-exclude venv --port 8000
```
Backend API will be available at `http://localhost:8000` (Swagger UI at `/docs`).

### 2. Setup Frontend
```bash
cd frontend
npm install
npm install framer-motion clsx tailwind-merge lucide-react

# Run the frontend
npm run dev
```
Frontend UI will be available at `http://localhost:3000`.

## ML Models Note
The NLP pipeline is currently configured to gracefully fallback to heuristic rules and exact dictionary matching if the large transformer models (`spacy en_core_web_trf`, `t5-small`, `all-MiniLM-L6-v2`) are not installed locally to save you Gigabytes of bandwidth during initial development.
You can enable them in `backend/app/nlp/` by uncommenting the model loading code once you have downloaded the weights.

---

## 🤖 Emoji ML Feature — Gloss → Emoji Translator

A neural sequence-to-sequence model converts raw ISL gloss text directly into
expressive emoji sequences, providing an alternative to the rule-based emoji
dictionary used in the main pipeline.

### Architecture

```
Gloss Input (text)
       ↓
  BERT Tokenizer  (bert-base-uncased, max 64 tokens)
       ↓
  Transformer Encoder  (BERT frozen weights)
       ↓
  Custom Transformer Decoder  (d_model=256, 4 heads, 3 layers)
       ↓
  Beam Search  (beam_size=4, max 20 tokens)
       ↓
  EmojiVocabulary.decode()
       ↓
  Emoji Output  "👤 🥣 🌅 🍽️"
```

### Trained Model Details

| Property        | Value                                 |
|-----------------|---------------------------------------|
| Architecture    | BERT encoder + custom Transformer decoder |
| Dataset         | PHOENIX-Weather 2014T (adapted)       |
| Training Loss   | 2.78 (cross-entropy)                  |
| Vocab Size      | see `backend/models/emoji_ml/saved_model/vocab.json` |
| Device          | Auto (CUDA if available, else CPU)    |
| Weights         | `backend/models/emoji_ml/saved_model/best_model.pt` |

### API Endpoint

```
POST  /api/convert-to-emoji
GET   /api/emoji-model-status     ← debug: check if model is loaded
```

**Request**
```json
{ "text": "yesterday home sourav breakfast eat" }
```

**Response (200)**
```json
{
  "success": true,
  "input":   "yesterday home sourav breakfast eat",
  "emoji":   "⬅️ 🏠 👤 🥣 🍽️",
  "model":   "GlossToEmojiModel",
  "tokens":  5
}
```

**Error responses**

| HTTP | Cause | Fix |
|------|-------|-----|
| `422` | Empty / missing `text` field | Send non-empty gloss string |
| `503` | Model weights not found | Run `python train.py` in `backend/models/emoji_ml/` |
| `500` | Inference crash (OOM, CUDA, …) | Check `backend/logs/signspeak.log` |

### Frontend Component

`frontend/src/components/translator/GlossToEmojiConverter.tsx`

The component is automatically mounted in the translate page below the existing
GlossDisplay and receives the gloss string as a prop.

**Features**

| Feature | Description |
|---------|-------------|
| Staggered bounce | Each emoji animates in with a 90ms stagger spring |
| History (10) | Last 10 conversions saved in `localStorage` |
| Favorites ⭐ | Star any result to bookmark it |
| Export PNG | Canvas-rendered image downloaded as `.png` |
| Share | Twitter, WhatsApp, copy-as-text |
| Settings | Animations on/off, sound on/off |
| Keyboard shortcuts | `Ctrl+Enter`, `F`, `H`, `?`, and more |
| Stats | Total conversions + today's count |
| Example prompts | One-click example glosses |
| Confetti 🎉 | Canvas confetti burst on every successful conversion |
| Sound effects | Web Audio API tones (optional, off by default) |

**Props**

```tsx
interface GlossToEmojiConverterProps {
  /** ISL gloss string from the main translator. e.g. "yesterday home eat" */
  glossText?: string;
}
```

### Testing

**PowerShell test suite (recommended)**
```powershell
# Run all tests
.\scripts\test_emoji_api.ps1

# Verbose mode (prints each response body)
.\scripts\test_emoji_api.ps1 -Verbose

# Custom backend URL
.\scripts\test_emoji_api.ps1 -BaseUrl "http://192.168.1.5:8000"
```

**Single curl-style tests**
```powershell
# Happy path
Invoke-RestMethod -Uri "http://localhost:8000/api/convert-to-emoji" `
  -Method POST -ContentType "application/json" `
  -Body '{"text":"I eat breakfast morning"}' | ConvertTo-Json

# Check model status without triggering inference
Invoke-RestMethod -Uri "http://localhost:8000/api/emoji-model-status" | ConvertTo-Json

# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health" | ConvertTo-Json
```

**Browser DevTools**
```js
// Paste in browser console while frontend is running
const r = await fetch("http://localhost:8000/api/convert-to-emoji", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "I eat breakfast morning" })
});
console.table(await r.json());
```

### Debug Logging

Set `LOG_LEVEL=DEBUG` in your `.env` file to see per-request timing:

```
INFO  📥 [emoji] Request from 127.0.0.1 — text[22 chars]: 'I eat breakfast morning'
DEBUG [emoji] Model retrieval took 0.3ms
INFO  ✅ [emoji] Done in 347ms — 4 token(s) → '👤 🥣 🌅 🍽️'
```

Watch live logs:
```powershell
Get-Content backend\logs\signspeak.log -Wait -Tail 30
```

### Common Error Scenarios

```
Error: 503 Service Unavailable
  "Emoji ML model weights not found"
  → cd backend/models/emoji_ml && python train.py

Error: 503 Service Unavailable
  "Could not import emoji_ml"
  → Start backend from backend/ directory: cd backend && python run.py

Error: CORS blocked in browser
  → backend/app/core/config.py already includes http://localhost:3000
    Check CORS_ORIGINS list if using a different port

Error: 422 Unprocessable Entity
  → You sent an empty "text" field — provide a non-empty gloss string

Error: Module 'torch' not found
  → pip install -r backend/requirements.txt
```

### File Map

```
backend/
  app/api/routes/emoji_routes.py     ← FastAPI router (POST /api/convert-to-emoji)
  app/main.py                        ← Registers emoji_routes.router
  models/emoji_ml/
    inference.py                     ← EmojiPredictor singleton + predict_emoji()
    model.py                         ← GlossToEmojiModel architecture
    vocabulary.py                    ← EmojiVocabulary encode/decode
    saved_model/
      best_model.pt                  ← Trained weights (gitignored if large)
      vocab.json                     ← Emoji vocabulary mapping

frontend/
  src/components/translator/
    GlossToEmojiConverter.tsx        ← Complete UI component
  src/app/translate/page.tsx         ← Mounts <GlossToEmojiConverter>

scripts/
  test_emoji_api.ps1                 ← Full PowerShell test suite
```
