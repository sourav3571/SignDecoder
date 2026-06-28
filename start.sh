#!/bin/bash
if [ -f "backend/venv/bin/python" ]; then
    (cd hf_deploy && ../backend/venv/bin/python -m uvicorn app_space:app --host 0.0.0.0 --port 8000 --reload) &
else
    (cd hf_deploy && ../backend/venv/Scripts/python.exe -m uvicorn app_space:app --host 0.0.0.0 --port 8000 --reload) &
fi
cd frontend && npm run dev
