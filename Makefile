SHELL := bash
ifneq (,$(wildcard .env))
include .env
export
endif


COMPOSE ?= docker compose
SETUP_SCRIPT ?= scripts/setup_weaviate.py

.PHONY: init-workspace run-local stop-local clean-local logs-local format lint

init-workspace:
	@echo "Initializing workspace..."
	@./scripts/setup_env.sh
	uv sync

# Start Weaviate, wait until healthy, run setup script, start API server, then start Streamlit
run-local:
	@echo "Starting Weaviate with Docker Compose..."
	@$(COMPOSE) up -d --wait --wait-timeout 300
	@echo "Running setup script to load sample vectors..."
	uv run python $(SETUP_SCRIPT)
	@echo "==============================================="
	@echo "Starting FastAPI server in background..."
	@uv run python scripts/run_api.py &
	@echo "Waiting for API server to start..."
	@sleep 5
	@echo "==============================================="
	@echo "Starting Streamlit app..."
	@uv run -m streamlit run streamlit_app/main.py


# Stop and remove containers (keeps volumes)
stop-local:
	@echo "Stopping FastAPI server..."
	@pkill -f "scripts/run_api.py" || true
	@echo "Stopping Weaviate stack..."
	@$(COMPOSE) down

# Stop and remove containers + volumes (wipes data)
clean-local:
	@echo "Stopping FastAPI server..."
	@pkill -f "scripts/run_api.py" || true
	@echo "Stopping Weaviate stack and removing volumes..."
	@$(COMPOSE) down -v

# Format code with Ruff
format:
	@echo "Formatting code with Ruff..."
	uv run ruff format .
	uv run ruff check --select I --fix .


# Lint code with Ruff
lint:
	@echo "Linting code with Ruff..."
	uv run ruff check . --fix
