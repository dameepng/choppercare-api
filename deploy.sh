#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

BRANCH="${BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUN_INGEST="${RUN_INGEST:-0}"

if [ ! -f .env ]; then
  echo "Missing .env in $APP_DIR"
  echo "Copy .env.example to .env and fill GROQ_API_KEY + DATABASE_URL first."
  exit 1
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python command not found: $PYTHON_BIN"
  exit 1
fi

if ! command -v pm2 >/dev/null 2>&1; then
  echo "pm2 is not installed. Install it first with: npm install -g pm2"
  exit 1
fi

mkdir -p logs

echo "==> Updating source code"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

if [ ! -d venv ]; then
  echo "==> Creating virtualenv"
  "$PYTHON_BIN" -m venv venv
fi

echo "==> Installing Python dependencies"
./venv/bin/python -m pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

if [ "$RUN_INGEST" = "1" ]; then
  echo "==> Ingesting BNPB documents"
  ./venv/bin/python scripts/ingest_docs.py
fi

echo "==> Restarting API via PM2"
pm2 startOrReload ecosystem.config.js --update-env
pm2 save

echo "API deployed successfully."
