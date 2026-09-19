@echo off
echo Starting SuryaDrishti Solar Flare Dashboard Suite...
echo.

:: 1. Start FastAPI backend (using virtual environment python)
echo [1/4] Starting FastAPI Ingestion Backend...
start "FastAPI Ingestion Backend" cmd /k "cd /d D:\PS15_SolarFlare\backend && ..\.venv\Scripts\python -m uvicorn data_ingest.main:app --host 127.0.0.1 --port 8000"

:: 2. Start Streamlit 2D Dashboard (using virtual environment streamlit)
echo [2/4] Starting Streamlit 2D Dashboard on port 8501...
start "Streamlit 2D Dashboard" cmd /k "cd /d D:\PS15_SolarFlare\frontend\dashboard && ..\..\.venv\Scripts\streamlit run dashboard.py --server.port 8501"

:: 3. Start Static HTTP Server on port 8080 for 3D Dashboard
echo [3/4] Starting Static HTTP Server on port 8080...
start "Static HTTP Server" cmd /k "cd /d D:\PS15_SolarFlare\frontend && ..\.venv\Scripts\python -m http.server 8080"

:: 4. Wait 3 seconds for initialization
echo [4/4] Waiting for services to initialize...
timeout /t 3 /nobreak >nul

:: 5. Open both dashboards in the browser
echo Opening dashboards...
start "" "http://localhost:8501"
start "" "http://localhost:8080/dashboard/dashboard.html"

echo.
echo All services launched! Keep the console windows open.
echo.
pause

