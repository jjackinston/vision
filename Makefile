# SellerVision AI — Local Development Commands
# Run `make help` to see all available commands

.PHONY: help setup dev dev-data dev-docker stop clean migrate migrate-down migrate-new seed install-backend install-frontend test test-backend test-frontend build-frontend build-docker logs shell-backend stripe-listen

SHELL := /bin/bash

# Compose file paths (actual locations in repo root)
COMPOSE_PROD := docker-compose.yml
COMPOSE_DEV  := docker-compose.dev.yml

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── First-time setup ──────────────────────────────────────────────────────────

setup: ## Full first-time setup: install deps, start dev services, migrate, seed
	@echo "Copying backend .env if missing..."
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env 2>/dev/null || cp backend/.env backend/.env; echo "  Edit backend/.env with your API keys."; fi
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Starting dev data services (Postgres + Redis)..."
	docker compose -f $(COMPOSE_DEV) up -d
	@echo "Waiting for Postgres..."
	@sleep 6
	@echo "Running database migrations..."
	cd backend && alembic upgrade head
	@echo "Seeding initial data..."
	cd backend && python run_seed.py
	@echo "Setup complete. Run 'make dev' to start the servers."

# ── Daily dev ─────────────────────────────────────────────────────────────────

dev-data: ## Start only the data layer (Postgres + Redis) via Docker
	docker compose -f $(COMPOSE_DEV) up -d

dev: ## Start backend API + frontend dev server (run 'make dev-data' first)
	@echo "Starting SellerVision AI dev environment..."
	@echo "  Backend on http://localhost:8000"
	@echo "  Frontend on http://localhost:3001"
	@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 & \
	 cd frontend && npm run dev

dev-docker: ## Start full production stack locally via Docker Compose
	docker compose -f $(COMPOSE_PROD) up

stop: ## Stop all Docker services (dev + prod)
	docker compose -f $(COMPOSE_DEV) down
	docker compose -f $(COMPOSE_PROD) down

# ── Database ──────────────────────────────────────────────────────────────────

migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

migrate-down: ## Rollback last migration
	cd backend && alembic downgrade -1

migrate-new: ## Create a new migration (usage: make migrate-new name=add_feature)
	cd backend && alembic revision --autogenerate -m "$(name)"

seed: ## Seed database with initial plans and demo data
	cd backend && python scripts/seed_plans.py

# ── Dependencies ──────────────────────────────────────────────────────────────

install-frontend: ## Install frontend npm packages
	cd frontend && npm install

install-backend: ## Install backend Python packages
	cd backend && pip install -r requirements.txt

# ── Testing ───────────────────────────────────────────────────────────────────

test-backend: ## Run backend tests
	cd backend && pytest tests/ -v --tb=short

test-frontend: ## Run frontend type-check and lint
	cd frontend && npm run type-check && npm run lint

test: test-backend test-frontend ## Run all tests

# ── Build ─────────────────────────────────────────────────────────────────────

build-frontend: ## Build frontend for production
	cd frontend && npm run build

build-docker: ## Build all Docker images
	docker compose -f $(COMPOSE_PROD) build

# ── Utilities ─────────────────────────────────────────────────────────────────

logs: ## Tail Docker logs
	docker compose -f $(COMPOSE_PROD) logs -f

shell-backend: ## Open a Python shell with app context
	cd backend && python -c "from app.core.config import settings; import IPython; IPython.embed()"

worker: ## Start Celery worker (run 'make dev-data' first)
	cd backend && celery -A app.workers.tasks worker --loglevel=info --concurrency=2

beat: ## Start Celery beat scheduler — run ONCE alongside the worker
	cd backend && celery -A app.workers.tasks beat --loglevel=info --scheduler celery.beat.PersistentScheduler

lint: ## Lint backend (ruff) + frontend (eslint)
	cd backend && ruff check app && cd ../frontend && npm run lint

stripe-listen: ## Start Stripe webhook listener (requires Stripe CLI)
	stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe

clean: ## Remove Docker volumes and node_modules
	docker compose -f $(COMPOSE_PROD) down -v
	rm -rf frontend/node_modules frontend/.next backend/__pycache__
