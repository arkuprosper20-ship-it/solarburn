@echo off
REM Stop and remove existing container if it exists
docker rm -f solar-dashboard-container >nul 2>&1

REM Build Docker image for 2D dashboard using parent directory (project root) as context
docker build -t solar-dashboard -f "%~dp0Dockerfile.dashboard" "%~dp0..\.."
if errorlevel 1 (
  echo Docker build failed.
  exit /b 1
)
REM Run container exposing port 8080 -> 80
docker run -d -p 8080:80 --name solar-dashboard-container solar-dashboard
if errorlevel 1 (
  echo Docker run failed.
  exit /b 1
)
echo Dashboard available at http://localhost:8080/dashboard_2d.html
