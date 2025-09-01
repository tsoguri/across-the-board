#!/usr/bin/env bash
set -euo pipefail

# Default .env file path (change to .environment if you prefer)
ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
  cat > "$ENV_FILE" <<'EOF'
# Override defaults if desired
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8080

# Path to setup script (relative to repo root)
SETUP_SCRIPT=scripts/setup_weaviate.py
JSON_PATH=scripts/data/clues.json
COLLECTION_NAME=CrosswordClues
BATCH_SIZE=200

KEY_CLUE=clue
KEY_ANSWER=answer
KEY_YEAR=year
KEY_PUBID=pubid
KEY_VECTOR=embedding_vector

EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B

# Optionally point to a Streamlit app to launch after setup
APP=streamlit_app/main.py

EOF

  echo "Created $ENV_FILE with default values."
else
  echo "$ENV_FILE already exists; leaving it untouched."
fi

set -a
source "$ENV_FILE"
set +a