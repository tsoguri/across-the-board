SHELL := bash
ifneq (,$(wildcard .env))
include .env
export
endif


COMPOSE ?= docker compose
WEAVIATE_SCRIPT ?= scripts/setup_weaviate.py
API_SCRIPT ?= scripts/run_api.py
STREAMLIT_PATH ?= streamlit_app/main.py
REACT_PATH ?= react_app

.PHONY: init-workspace run-local run-streamlit run-react stop-local clean-local logs-local format lint

init-workspace:
	@echo "Initializing workspace..."
	@./scripts/setup_env.sh
	uv sync

# Start Weaviate, wait until healthy, run setup script, start API server, then start Streamlit
run-streamlit:
	@echo "Starting Weaviate with Docker Compose..."
	@$(COMPOSE) up -d --wait --wait-timeout 300
	@echo "Running setup script to load sample vectors..."
	uv run python $(WEAVIATE_SCRIPT)
	@echo "==============================================="
	@echo "Starting FastAPI server in background..."
	@uv run python $(API_SCRIPT) &
	@echo "Waiting for API server to start..."
	@sleep 5
	@echo "==============================================="
	@echo "Starting Streamlit app..."
	@uv run -m streamlit run $(STREAMLIT_PATH)

# Start Weaviate, wait until healthy, run setup script, start API server, then start React
run-react:
	@echo "Starting Weaviate with Docker Compose..."
	@$(COMPOSE) up -d --wait --wait-timeout 300
	@echo "Running setup script to load sample vectors..."
	uv run python $(WEAVIATE_SCRIPT)
	@echo "==============================================="
	@echo "Starting FastAPI server in background..."
	@uv run python $(API_SCRIPT) &
	@echo "Waiting for API server to start..."
	@sleep 5
	@echo "==============================================="
	@echo "Starting React app..."
	@cd $(REACT_PATH) && npm run dev

# Stop and remove containers (keeps volumes)
stop-local:
	@echo "Stopping FastAPI server..."
	@pkill -f "$(API_SCRIPT)" || true
	@echo "Stopping Weaviate stack..."
	@$(COMPOSE) down

# Stop and remove containers + volumes (wipes data)
clean-local:
	@echo "Stopping FastAPI server..."
	@pkill -f "$(API_SCRIPT)" || true
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
