#!/usr/bin/env bash
# LinkedIn Jobs Scraper — installer
set -euo pipefail

cd "$(dirname "$0")"

echo "==> Checking dependencies..."
command -v curl   >/dev/null || { echo "❌ curl not found (install: apt install curl)"; exit 1; }
command -v python3 >/dev/null || { echo "❌ python3 not found"; exit 1; }

echo "==> Setting up virtualenv (.venv)..."
if python3 -c "import venv" 2>/dev/null && python3 -m venv .venv; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
  echo "==> Installing Python deps into .venv (websocket-client for cookie injection only)..."
  pip install -q -r requirements.txt
else
  rm -rf .venv 2>/dev/null || true
  echo "⚠️  venv indisponível — instalando no Python global..."
  python3 -m pip install -q -r requirements.txt 2>/dev/null \
    || python3 -m pip install -q --break-system-packages -r requirements.txt
fi

echo "==> Preparing data dir..."
mkdir -p data

echo "==> Smoke test (guest API, 1 page)..."
python3 scripts/scrape_jobs.py --keywords "Analista de Sistemas" --geoId 106057199 --pages 1 --out data/smoke_test.json

COUNT=$(python3 -c "import json; print(len(json.load(open('data/smoke_test.json'))))")
if [ "$COUNT" -gt 0 ]; then
  echo "✅ OK — $COUNT vagas coletadas no smoke test"
  echo ""
  echo "Próximos passos:"
  if [ -f .venv/bin/activate ]; then
    echo "  source .venv/bin/activate"
  fi
  echo "  python3 scripts/scrape_jobs.py --remote --last24h --pages 5"
  echo "  python3 scripts/generate_dashboard.py data/linkedin_jobs.json data/dashboard.html"
else
  echo "❌ Smoke test retornou 0 vagas — verifique conectividade com linkedin.com"
  exit 1
fi
