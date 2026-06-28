@echo off
start cmd /k "cd backend && call venv\Scripts\activate && python run.py"
start cmd /k "cd frontend && npm run dev"
