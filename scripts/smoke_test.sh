#!/usr/bin/env bash
# Phase 0/1 smoke test — verifies the gateway is up and Ollama + both models are
# reachable. Assumes the backend is running (see README). Pass the port as $1
# (default 8000).
set -euo pipefail

PORT="${1:-8000}"
BASE="http://127.0.0.1:${PORT}"

echo "== /health =="
curl -fsS "${BASE}/health" && echo

echo "== /health/ollama =="
curl -fsS "${BASE}/health/ollama" && echo

echo "== /api/chat (benign) =="
curl -fsS -X POST "${BASE}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"smoke-1","message":"What roaming packs do you offer?"}' && echo

echo "== /api/chat (empty -> expect HTTP 422) =="
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"smoke-2","message":""}')
echo "HTTP ${code}"
[ "${code}" = "422" ] || { echo "FAIL: expected 422"; exit 1; }

echo "All smoke checks passed."
