#!/usr/bin/env python3
"""
Script to run the FastAPI server locally.
This will start the API server with hot-reload enabled for development.
"""

import os
import sys

import uvicorn

# Add the project root to Python path so 'api' module can be found
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main() -> int:
    print("Starting Across the Board API Server...")
    print("- Swagger UI will be available at: http://localhost:8000/docs")
    print("- OpenAPI spec will be available at: http://localhost:8000/openapi.json")

    try:
        uvicorn.run(
            "api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
        )
        return 0
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting API server: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
