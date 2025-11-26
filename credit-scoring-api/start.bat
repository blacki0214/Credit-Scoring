@echo off
REM Startup script for Credit Scoring API (Windows)

echo ============================================
echo    Credit Scoring API - Startup Script     
echo ============================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo Docker is running

REM Check if model files exist
if not exist "models\lgb_model_optimized.pkl" (
    echo ERROR: Model file not found
    echo Please ensure models\lgb_model_optimized.pkl exists
    pause
    exit /b 1
)

if not exist "models\ensemble_comparison_metadata.pkl" (
    echo ERROR: Metadata file not found
    echo Please ensure models\ensemble_comparison_metadata.pkl exists
    pause
    exit /b 1
)

echo Model files found

REM Stop existing containers
echo.
echo Stopping existing containers...
docker-compose down

REM Build and start
echo.
echo Building and starting API...
docker-compose up --build -d

REM Wait for container to be ready
echo.
echo Waiting for API to be ready...
timeout /t 10 /nobreak >nul

REM Check if container is running
docker ps -q -f name=credit-scoring-api >nul 2>&1
if errorlevel 1 (
    echo ERROR: Container failed to start
    echo Check logs: docker-compose logs
    pause
    exit /b 1
)

echo Container is running

REM Test health endpoint
echo.
echo Testing health endpoint...
timeout /t 5 /nobreak >nul

curl -f -s http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: Container is running but API is not responding yet
    echo Please wait a moment and check: http://localhost:8000/docs
) else (
    echo API is healthy
    echo.
    echo ============================================
    echo    API is ready!
    echo ============================================
    echo.
    echo Documentation: http://localhost:8000/docs
    echo Health Check:  http://localhost:8000/api/health
    echo Logs:          docker-compose logs -f
    echo.
    echo To stop: docker-compose down
    echo ============================================
)

pause
