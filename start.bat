@echo off
start /b cmd /c "cd backend && call venv\Scripts\activate && python run.py"
cd frontend && npm run dev
