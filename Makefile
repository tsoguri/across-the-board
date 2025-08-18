SHELL := bash
ifneq (,$(wildcard .env))
include .env
export
endif


COMPOSE ?= docker compose

.PHONY: init-workspace run-local stop-local clean-local logs-local format lint

init-workspace:
	@echo "Initializing workspace..."
	@./scripts/setup_env.sh
	uv sync

# Start Weaviate, wait until healthy, run setup script, then (optionally) start Streamlit
run-local:
	@echo "Starting Weaviate with Docker Compose..."
	@$(COMPOSE) up -d --wait --wait-timeout 300
	@echo "Running setup script to load sample vectors..."
	uv run python $(SETUP_SCRIPT)
	@if [ -n "$(APP)" ]; then \
		echo "Starting Streamlit app: $(APP)"; \
		uv run streamlit run -m $(APP); \
	else \
		echo "No APP specified. Skipping Streamlit."; \
	fi


# Stop and remove containers (keeps volumes)
stop-local:
	@echo "Stopping Weaviate stack..."
	@$(COMPOSE) down

# Stop and remove containers + volumes (wipes data)
clean-local:
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
	uv run ruff check .
