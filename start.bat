@echo off
start /b cmd /c "cd hf_deploy && ..\backend\venv\Scripts\python.exe -m uvicorn app_space:app --host 0.0.0.0 --port 8000 --reload"
cd frontend && npm run dev
