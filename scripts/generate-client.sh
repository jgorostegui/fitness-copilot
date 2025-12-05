#!/usr/bin/env bash
# Generate OpenAPI client from backend schema
# Usage: ./scripts/generate-client.sh [--local]
#   --local: Use local uv instead of Docker (requires backend venv)

set -e
set -x

SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "$1" == "--local" ]]; then
    # Local mode: use uv directly
    uv run --directory "$PROJECT_ROOT/backend" python -c \
        "import app.main; import json; print(json.dumps(app.main.app.openapi()))" \
        > "$PROJECT_ROOT/frontend/openapi.json"
else
    # Docker mode: use running backend container
    docker compose exec backend python -c \
        "import app.main; import json; print(json.dumps(app.main.app.openapi()))" \
        > "$PROJECT_ROOT/frontend/openapi.json"
fi

# Generate TypeScript client
npm --prefix "$PROJECT_ROOT/frontend" run generate-client

# Format generated code (run from frontend dir to use correct biome config)
cd "$PROJECT_ROOT/frontend"
npx biome format --write ./src/client || echo "Biome format skipped (client may be in ignore list)"
