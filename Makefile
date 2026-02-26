##############################################
# Travel AI - Makefile
# One-click commands for development & deployment
##############################################

.PHONY: help up down build test logs deploy-k8s clean validate

# Default target
help: ## Show this help
	@echo =============================================
	@echo   Travel AI - Available Commands
	@echo =============================================
	@echo   make up          - Start all services (Docker Compose)
	@echo   make down        - Stop all services
	@echo   make build       - Build Docker images
	@echo   make test        - Run backend tests
	@echo   make logs        - Tail logs from all services
	@echo   make validate    - Validate K8s manifests (dry-run)
	@echo   make deploy-k8s  - Deploy to Kubernetes cluster
	@echo   make clean       - Remove containers, volumes, and images
	@echo =============================================

# ─── Docker Compose ─────────────────────────

up: ## Build and start all services
	@echo [*] Validating environment...
	@if not exist backend\.env ( echo [ERROR] backend\.env not found! Create it from .env.example & exit /b 1 )
	docker-compose up --build -d
	@echo.
	@echo [OK] Services are starting...
	@echo   Frontend: http://localhost:3000
	@echo   Backend:  http://localhost:8000
	@echo   MongoDB:  localhost:27017

down: ## Stop all services
	docker-compose down
	@echo [OK] All services stopped.

build: ## Build Docker images without starting
	docker-compose build

logs: ## Tail logs from all running services
	docker-compose logs -f

# ─── Testing ────────────────────────────────

test: ## Run backend tests inside Docker
	docker-compose run --rm backend python -m pytest --tb=short -q

# ─── Kubernetes ─────────────────────────────

validate: ## Validate all K8s manifests (dry-run)
	kubectl apply --dry-run=client -f k8s/configmap.yaml
	kubectl apply --dry-run=client -f k8s/secret.yaml
	kubectl apply --dry-run=client -f k8s/mongo.yaml
	kubectl apply --dry-run=client -f k8s/redis.yaml
	kubectl apply --dry-run=client -f k8s/deployment.yaml
	kubectl apply --dry-run=client -f k8s/service.yaml
	kubectl apply --dry-run=client -f k8s/frontend.yaml
	kubectl apply --dry-run=client -f k8s/ingress.yaml
	kubectl apply --dry-run=client -f k8s/network-policies.yaml
	kubectl apply --dry-run=client -f k8s/pod-disruption-budget.yaml
	@echo [OK] All manifests are valid.

deploy-k8s: validate ## Deploy to Kubernetes cluster
	@echo [*] Deploying to Kubernetes...
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secret.yaml
	kubectl apply -f k8s/mongo.yaml
	kubectl apply -f k8s/redis.yaml
	kubectl apply -f k8s/network-policies.yaml
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/service.yaml
	kubectl apply -f k8s/frontend.yaml
	kubectl apply -f k8s/ingress.yaml
	kubectl apply -f k8s/pod-disruption-budget.yaml
	@echo [OK] Deployment complete! Run 'kubectl get pods' to check status.

# ─── Cleanup ────────────────────────────────

clean: down ## Remove containers, volumes, and dangling images
	docker-compose down -v --remove-orphans
	docker image prune -f
	@echo [OK] Cleanup complete.
