"""
Quick setup guide for SignSpeak Phase 1 Foundation
"""

PHASE 1: FOUNDATION - COMPLETE! ✓
═══════════════════════════════════════════════════════════════════

WHAT'S BEEN BUILT:

1. ✓ Project Structure
   backend/
   ├── app/
   │   ├── core/              # Database, Redis, Config
   │   ├── api/v1/            # FastAPI routes  
   │   ├── models/            # ORM models
   │   ├── nlp/               # NLP modules (for Phase 2)
   │   └── services/          # Business logic
   ├── requirements.txt       # All dependencies
   └── run.py                # Entry point

2. ✓ Configuration System
   - app/core/config.py      # Settings from .env
   - .env.example            # Template with all variables
   - Environment-aware (dev/prod)

3. ✓ Database Connections
   - PostgreSQL async (SQLAlchemy)
   - Redis cache
   - MongoDB ready (Phase 2+)
   - Health checks included

4. ✓ FastAPI Application
   - Proper lifespan management
   - CORS middleware
   - Error handling
   - API documentation (/docs)

5. ✓ Health Check Endpoints
   - GET /health              # Full system status
   - GET /health/ready        # Kubernetes readiness
   - GET /health/live         # Kubernetes liveness
   - GET /version             # Version info
   - GET /                    # Root info

6. ✓ Docker Support
   - docker-compose.yml       # Local dev environment
   - Dockerfile              # Production image
   - PostgreSQL + MongoDB + Redis setup
   - Automatic healthchecks

7. ✓ Database Models (ORM)
   - User                    # For auth (Phase 5+)
   - TranslationHistory      # Logs all translations
   - EmojiMapping            # For Phase 3
   - NLPModel                # Model versioning & metrics

═══════════════════════════════════════════════════════════════════
QUICK START - LOCAL DEVELOPMENT
═══════════════════════════════════════════════════════════════════

STEP 1: Setup Environment
────────────────────────────────────────────────────────────────────
cd backend
cp ../.env.example ../.env
# Edit .env with your settings (defaults work for local dev)

STEP 2: Install Python Dependencies
────────────────────────────────────────────────────────────────────
python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
pip install -r requirements.txt

STEP 3: Start Services with Docker Compose
────────────────────────────────────────────────────────────────────
cd ..
docker-compose up -d

This starts:
- PostgreSQL (port 5432)
- MongoDB (port 27017)
- Redis (port 6379)

STEP 4: Run API Server
────────────────────────────────────────────────────────────────────
cd backend
python run.py

Or with auto-reload:
uvicorn app.main:app --reload

API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

STEP 5: Check Health
────────────────────────────────────────────────────────────────────
curl http://localhost:8000/health

Response should show:
{
  "status": "healthy",
  "services": {
    "postgresql": {"status": "online"},
    "redis": {"status": "online"},
    "nlp_models": {"status": "not_initialized"}
  }
}

═══════════════════════════════════════════════════════════════════
PROJECT STRUCTURE EXPLAINED
═══════════════════════════════════════════════════════════════════

backend/
├── app/
│   ├── core/                    # Infrastructure layer
│   │   ├── config.py           # Settings from .env
│   │   ├── database.py         # PostgreSQL connections
│   │   └── redis.py            # Cache operations
│   │
│   ├── api/v1/                 # API endpoints (Phase 1+)
│   │   └── health.py           # Health check endpoints
│   │
│   ├── models/                 # Data layer
│   │   ├── database.py         # ORM models (SQLAlchemy)
│   │   └── schemas.py          # Request/Response (Pydantic)
│   │
│   ├── nlp/                    # NLP pipeline (Phase 2+)
│   │   ├── analyzer.py         # spaCy NLP
│   │   ├── preprocessor.py     # Text cleaning
│   │   ├── reorderer.py        # Sign language grammar
│   │   ├── emoji_mapper.py     # Emoji mapping logic
│   │   └── gloss_generator.py  # Gloss generation
│   │
│   ├── services/               # Business logic (Phase 2+)
│   │   └── translation_service.py  # Main translation pipeline
│   │
│   └── main.py                 # FastAPI app entry

Configuration:
├── .env                        # Local environment variables
├── .env.example               # Template for .env
└── docker-compose.yml         # Local dev environment

═══════════════════════════════════════════════════════════════════
KEY DESIGN DECISIONS IN PHASE 1
═══════════════════════════════════════════════════════════════════

1. ASYNC/AWAIT EVERYWHERE
   Why: FastAPI is async-native; better performance under load
   Benefit: Single server handles many concurrent requests

2. SQLAlchemy ORM with PostgreSQL
   Why: Type-safe, queryable, scalable relational data
   Benefit: Translation history for research/analytics

3. Redis for Caching + Task Queue
   Why: Fast cache for NLP results; Celery for async tasks
   Benefit: Reduces ML model latency significantly

4. Pydantic for API Validation
   Why: Type hints + automatic validation + OpenAPI docs
   Benefit: Catch bugs early; great developer experience

5. Modular Architecture
   Why: Clean separation of concerns
   Benefit: Easy to test, replace components, scale independently

6. Health Checks from Day 1
   Why: Production-ready monitoring
   Benefit: Deploy with confidence; easy troubleshooting

═══════════════════════════════════════════════════════════════════
WHAT'S READY FOR PHASE 2
═══════════════════════════════════════════════════════════════════

Phase 2 will build the NLP Core on this foundation:
- Text preprocessor (spell check, contractions, cleaning)
- spaCy semantic analyzer (NER, POS, dependency parsing)
- Sign language reorderer (grammar transformation)
- All with proper error handling and caching

The API structure is ready to accept:
POST /api/v1/translate
{
  "text": "user input here",
  "include_details": true
}

Returns will include timing, confidence scores, debug info.

═══════════════════════════════════════════════════════════════════
NEXT STEPS
═══════════════════════════════════════════════════════════════════

1. Start local services:
   docker-compose up -d

2. Verify everything works:
   curl http://localhost:8000/health

3. Ready for Phase 2:
   Building the NLP Core!

═══════════════════════════════════════════════════════════════════
"""

print(__doc__)
