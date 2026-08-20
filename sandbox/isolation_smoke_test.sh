#!/usr/bin/env bash
# Mirror Maze isolation smoke test (Phase 3 Step 3.1; a preview of the Phase 6
# integrity audit). Proves, from INSIDE the decoy container, that its only
# reachable network peer is Ollama-via-proxy — no host, no internet, no gateway.
#
# Usage: bash sandbox/isolation_smoke_test.sh [gateway_port]
set -uo pipefail

COMPOSE="docker compose -f sandbox/docker-compose.sandbox.yml"
GATEWAY_PORT="${1:-8055}"
PASS=0; FAIL=0

# Run a short python probe inside the decoy container; prints REACHABLE/BLOCKED.
probe() {  # $1=label  $2=python-connect-expression  $3=expected(REACHABLE|BLOCKED)
  local label="$1" expr="$2" expected="$3"
  local out
  out=$($COMPOSE exec -T mirror_maze python -c "$expr" 2>/dev/null)
  if [ "$out" = "$expected" ]; then
    echo "  PASS  $label -> $out (expected $expected)"; PASS=$((PASS+1))
  else
    echo "  FAIL  $label -> ${out:-<error>} (expected $expected)"; FAIL=$((FAIL+1))
  fi
}

echo "== Mirror Maze isolation smoke test =="

# 1. Ollama via the proxy MUST be reachable (the decoy needs to generate). Send
#    the same Host header the decoy uses, so Ollama's DNS-rebind check passes.
probe "Ollama via proxy (needed)" \
'import httpx
try:
    r=httpx.get("http://ollama-proxy:11434/api/tags",headers={"Host":"localhost:11434"},timeout=5)
    print("REACHABLE" if r.status_code==200 else "BLOCKED")
except Exception: print("BLOCKED")' \
"REACHABLE"

# 2. The internet MUST be blocked.
probe "Internet egress (example.com)" \
'import httpx
try:
    httpx.get("https://example.com",timeout=5); print("REACHABLE")
except Exception: print("BLOCKED")' \
"BLOCKED"

# 3. The production gateway on the host MUST be unreachable.
probe "Host gateway :$GATEWAY_PORT" \
"import httpx
try:
    httpx.get('http://host.docker.internal:${GATEWAY_PORT}/health',timeout=5); print('REACHABLE')
except Exception: print('BLOCKED')" \
"BLOCKED"

# 4. Direct host Ollama (bypassing the proxy) MUST be unreachable.
probe "Direct host Ollama (bypass proxy)" \
'import httpx
try:
    httpx.get("http://host.docker.internal:11434/api/tags",timeout=5); print("REACHABLE")
except Exception: print("BLOCKED")' \
"BLOCKED"

# 5. The decoy runs as a non-root user.
uid=$($COMPOSE exec -T mirror_maze id -u 2>/dev/null | tr -d '\r')
if [ "$uid" != "0" ] && [ -n "$uid" ]; then
  echo "  PASS  Non-root process -> uid=$uid"; PASS=$((PASS+1))
else
  echo "  FAIL  Non-root process -> uid=${uid:-<error>}"; FAIL=$((FAIL+1))
fi

echo "== $PASS passed, $FAIL failed =="
[ "$FAIL" -eq 0 ] && echo "ISOLATION OK" || { echo "ISOLATION FAILED"; exit 1; }
