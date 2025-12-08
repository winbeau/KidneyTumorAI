#!/usr/bin/env bash
set -euo pipefail

# Start the FastAPI backend using uv for dependency management.
# - Creates/uses a local venv (override with VENV_PATH).
# - Installs deps once (skips if FastAPI already importable, unless FORCE_INSTALL=1).
# - Starts uvicorn with env vars from backend/.env if present.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
VENV_PATH="${VENV_PATH:-$ROOT_DIR/.venv}"
UV_BIN="${UV_BIN:-uv}"

if ! command -v "$UV_BIN" >/dev/null 2>&1; then
  echo "uv not found. Install from https://github.com/astral-sh/uv and retry." >&2
  exit 1
fi

echo "Repo root: $ROOT_DIR"
echo "Backend dir: $BACKEND_DIR"
echo "Using venv: $VENV_PATH"

# Create or reuse the venv managed by uv
"$UV_BIN" venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"

NEED_INSTALL=0
if [ "${FORCE_INSTALL:-0}" = "1" ]; then
  NEED_INSTALL=1
elif ! python - <<'PY' >/dev/null 2>&1
import importlib
import sys
for mod in ("fastapi", "sqlalchemy", "nibabel"):
    importlib.import_module(mod)
PY
then
  NEED_INSTALL=1
fi

if [ "$NEED_INSTALL" = "1" ]; then
  echo "Installing backend dependencies with uv..."
  "$UV_BIN" pip install -r "$BACKEND_DIR/requirements.txt"
else
  echo "Dependencies already present; skipping install (set FORCE_INSTALL=1 to override)."
fi

cd "$BACKEND_DIR"

ENV_FILE_ARGS=()
if [ -f ".env" ]; then
  ENV_FILE_ARGS=(--env-file ".env")
fi

exec "$UV_BIN" run "${ENV_FILE_ARGS[@]}" uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
