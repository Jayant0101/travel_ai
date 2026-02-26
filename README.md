# 🌍 Travel AI — Intelligent Travel Booking Agent

An AI-powered travel itinerary generator and booking platform, built with **FastAPI**, **React**, **MongoDB**, and **Google Gemini AI**.

---

## 📁 Project Structure

```
Travel Ai/
├── backend/                 # FastAPI backend (Python 3.11)
│   ├── Dockerfile           # Multi-stage, non-root production image
│   ├── .dockerignore
│   ├── server.py            # Main FastAPI application
│   ├── models.py            # Pydantic data models
│   ├── auth.py              # JWT authentication
│   ├── itinerary_service.py # Google Gemini AI integration
│   ├── requirements.txt
│   └── .env                 # Environment variables (DO NOT commit)
│
├── frontend/                # React (CRACO) frontend
│   ├── Dockerfile           # Multi-stage: Node build → Nginx serve
│   ├── .dockerignore
│   ├── nginx.conf           # Production Nginx config with security headers
│   └── ...                  # React app source files
│
├── k8s/                     # Kubernetes manifests
│   ├── deployment.yaml      # Backend Deployment (3 replicas, resource limits)
│   ├── service.yaml         # Backend ClusterIP Service + HPA
│   ├── frontend.yaml        # Frontend Deployment + Service + HPA
│   ├── mongo.yaml           # MongoDB StatefulSet with PVC
│   ├── ingress.yaml         # Nginx Ingress (with TLS scaffold)
│   ├── secret.yaml          # K8s Secrets template
│   └── network-policies.yaml# Zero-trust network policies
│
├── docker-compose.yml       # Local dev: Backend + Frontend + MongoDB
├── Makefile                 # One-click commands
├── start.bat                # Windows one-click starter
├── start.sh                 # Linux/macOS one-click starter
└── README.md                # This file
```

---

## 🚀 Quick Start (One-Click)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- Backend `.env` file configured (see below)

### Windows
```batch
start.bat
```

### Linux / macOS
```bash
chmod +x start.sh
./start.sh
```

### Using Make
```bash
make up        # Build & start all services
make down      # Stop all services
make logs      # Tail live logs
make test      # Run backend tests
make clean     # Remove everything (containers, volumes, images)
```

---

## ⚙️ Environment Setup

### `backend/.env`
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="travel_agent_db"
CORS_ORIGINS="*"
GOOGLE_API_KEY="your-google-api-key"
JWT_SECRET="a-strong-random-secret"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> **Note:** When using Docker Compose, `MONGO_URL` is automatically overridden to `mongodb://mongodb:27017`.

---

## 🐳 Docker Architecture

| Service      | Port  | Description                        |
|-------------|-------|------------------------------------|
| `frontend`  | 3000  | Nginx serving React + API proxy    |
| `backend`   | 8000  | FastAPI with 4 Uvicorn workers     |
| `mongodb`   | 27017 | MongoDB 7.0 with persistent volume |

### Health Checks
- **MongoDB**: `mongosh --eval "db.adminCommand('ping')"` every 10s
- **Backend**: `GET /api/health` every 15s (waits for MongoDB healthy first)
- **Frontend**: `curl http://localhost:80/` every 15s (waits for Backend healthy first)

### Security Features
- ✅ Non-root container users
- ✅ Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- ✅ Gzip compression
- ✅ Static asset caching (1 year, immutable)

---

## ☸️ Kubernetes Deployment

### Prerequisites
- `kubectl` configured with a cluster
- Docker images pushed to your registry

### Deploy
```bash
# 1. Update image names in deployment.yaml & frontend.yaml
# 2. Update secrets in k8s/secret.yaml
# 3. Update domain in k8s/ingress.yaml

# Validate first
make validate

# Deploy
make deploy-k8s
```

### Scaling
The system scales automatically via **Horizontal Pod Autoscalers**:

| Component  | Min | Max | CPU Target | Memory Target |
|-----------|-----|-----|-----------|---------------|
| Backend   | 3   | 10  | 65%       | 80%           |
| Frontend  | 2   | 8   | 70%       | —             |

### Network Security (Zero-Trust)
- **Default**: All traffic denied
- **Frontend**: Accepts ingress, can only talk to Backend
- **Backend**: Accepts from Frontend + Ingress, can reach MongoDB + external HTTPS (Gemini API)
- **MongoDB**: Only accepts connections from Backend

---

## 🧪 Testing

```bash
# Run backend tests locally
cd backend && python -m pytest --tb=short -q

# Run tests via Docker
make test
```

---

## 📋 API Endpoints

| Method | Endpoint                     | Auth | Description           |
|--------|------------------------------|------|-----------------------|
| POST   | `/api/auth/register`         | No   | Register new user     |
| POST   | `/api/auth/login`            | No   | Login user            |
| GET    | `/api/auth/me`               | Yes  | Get current user      |
| POST   | `/api/trips/generate`        | Yes  | Generate AI itinerary |
| GET    | `/api/trips`                 | Yes  | List user trips       |
| GET    | `/api/trips/{id}`            | Yes  | Get specific trip     |
| PUT    | `/api/trips/{id}/confirm`    | Yes  | Confirm trip          |
| POST   | `/api/bookings`              | Yes  | Create booking        |
| GET    | `/api/bookings/trip/{id}`    | Yes  | Get trip bookings     |
| POST   | `/api/payments/create`       | Yes  | Create payment order  |
| POST   | `/api/payments/verify`       | Yes  | Verify payment        |
| GET    | `/api/health`                | No   | Health check          |
