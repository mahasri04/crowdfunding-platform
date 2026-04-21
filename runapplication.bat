@echo off
echo Starting backend...
start cmd /k "call env\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000"
echo Starting frontend...
cd frontend
start cmd /k "npm start"
cd ..
