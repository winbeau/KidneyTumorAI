#!/usr/bin/env bash
set -euo pipefail

# Quick bootstrap + run for the FastAPI backend.
# - Creates/uses a local venv (override with VENV_PATH).
# - Installs backend requirements (skip with SKIP_PIP=1).
# - Runs `python run.py` (extra args forwarded to run.py; run.py currently ignores them).

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
VENV_PATH="${VENV_PATH:-$ROOT_DIR/.venv}"

echo "Repo root: $ROOT_DIR"
echo "Backend dir: $BACKEND_DIR"
echo "Using venv: $VENV_PATH"

if [ ! -d "$VENV_PATH" ]; then
  python -m venv "$VENV_PATH"
fi
source "$VENV_PATH/bin/activate"

if [ "${SKIP_PIP:-0}" != "1" ]; then
  pip install --upgrade pip
  pip install -r "$BACKEND_DIR/requirements.txt"
fi

cd "$BACKEND_DIR"
exec python run.py "$@"
