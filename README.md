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
