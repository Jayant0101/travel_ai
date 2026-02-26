@echo off
cd backend
venv\Scripts\uvicorn server:app --reload
pause
