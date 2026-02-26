@echo off
REM =============================================
REM   Travel AI - One-Click Start (Windows)
REM =============================================

echo [*] Checking prerequisites...

REM Check Docker is installed and running
docker version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not running!
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check docker-compose
docker-compose version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not available!
    pause
    exit /b 1
)

REM Check backend .env exists
if not exist "backend\.env" (
    echo [ERROR] backend\.env file is missing!
    echo Please create it with the required environment variables.
    echo   Required keys: MONGO_URL, DB_NAME, GOOGLE_API_KEY, JWT_SECRET
    pause
    exit /b 1
)

echo [OK] All prerequisites met.
echo.
echo [*] Building and starting all services...

docker-compose up --build -d

if errorlevel 1 (
    echo [ERROR] Failed to start services!
    echo Run 'docker-compose logs' for details.
    pause
    exit /b 1
)

echo.
echo =============================================
echo   Travel AI is running!
echo =============================================
echo   Frontend:   http://localhost:3000
echo   Backend:    http://localhost:8000/api
echo   MongoDB:    localhost:27017
echo.
echo   To view logs:   docker-compose logs -f
echo   To stop:        docker-compose down
echo =============================================

pause
