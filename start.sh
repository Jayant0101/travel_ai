#!/usr/bin/env bash
# =============================================
#   Travel AI - One-Click Start (Linux/macOS)
# =============================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[*] Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not installed!${NC}"
    echo "Install: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}[ERROR] Docker daemon is not running!${NC}"
    exit 1
fi

# Check docker-compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}[ERROR] Docker Compose is not available!${NC}"
    exit 1
fi

# Check .env
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}[ERROR] backend/.env file is missing!${NC}"
    echo "  Required: MONGO_URL, DB_NAME, GOOGLE_API_KEY, JWT_SECRET"
    exit 1
fi

echo -e "${GREEN}[OK] All prerequisites met.${NC}"
echo ""
echo -e "${YELLOW}[*] Building and starting all services...${NC}"

docker-compose up --build -d

echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}  Travel AI is running!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo "  Frontend:   http://localhost:3000"
echo "  Backend:    http://localhost:8000/api"
echo "  MongoDB:    localhost:27017"
echo ""
echo "  To view logs:   docker-compose logs -f"
echo "  To stop:        docker-compose down"
echo -e "${GREEN}=============================================${NC}"
