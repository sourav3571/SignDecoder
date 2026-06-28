#!/bin/bash
(cd backend && source venv/Scripts/activate && python run.py) &
cd frontend && npm run dev
