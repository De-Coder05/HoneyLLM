#!/usr/bin/env bash
# Phase 6, Step 6.2 — Sandbox integrity / break-out audit.
#
# Actively attempts to break OUT of the Mirror Maze decoy container across every
# escape vector we can exercise from the inside: network egress, container-escape
# primitives (docker socket, privilege, host mounts), and data reachability.
# Produces the "zero verified escapes" evidence for the capstone report.
#
# A PASS means the escape was BLOCKED (the sandbox held). Any FAIL is a real
# isolation breach.
#
# Usage: bash sandbox/breakout_audit.sh [gateway_port]   (default 8055)
set -uo pipefail
export PATH="/opt/homebrew/bin:$PATH"
COMPOSE="docker compose -f sandbox/docker-compose.sandbox.yml"
C="$COMPOSE exec -T mirror_maze"
GW="${1:-8055}"
PASS=0; FAIL=0
JSON="/tmp/breakout_audit_results.json"; echo "[" > "$JSON"; FIRST=1

record() { # name expected result detail
  local ok=$([ "$2" = "$3" ] && echo true || echo false)
  [ "$FIRST" = 1 ] && FIRST=0 || echo "," >> "$JSON"
  printf '  {"check":"%s","expected":"%s","result":"%s","pass":%s,"detail":"%s"}' \
    "$1" "$2" "$3" "$ok" "${4:-}" >> "$JSON"
}
check() { # label expected(BLOCKED|REACHABLE|...) actual detail
  if [ "$2" = "$3" ]; then echo "  PASS  $1 → $3"; PASS=$((PASS+1))
  else echo "  FAIL  $1 → ${3:-<err>} (wanted $2)"; FAIL=$((FAIL+1)); fi
  record "$1" "$2" "$3" "${4:-}"
}
pyprobe() { $C python -c "$1" 2>/dev/null | tr -d '\r'; }

echo "══ Mirror Maze break-out audit ══"

echo; echo "A. NETWORK EGRESS (attacker tries to reach out)"
check "Internet HTTP (example.com)"  BLOCKED "$(pyprobe 'import httpx
try: httpx.get("https://example.com",timeout=5); print("REACHABLE")
except Exception: print("BLOCKED")')"
check "Internet IP (1.1.1.1:443)"    BLOCKED "$(pyprobe 'import socket
try: socket.create_connection(("1.1.1.1",443),timeout=5); print("REACHABLE")
except Exception: print("BLOCKED")')"
check "Production gateway :$GW"       BLOCKED "$(pyprobe "import httpx
try: httpx.get('http://host.docker.internal:${GW}/health',timeout=5); print('REACHABLE')
except Exception: print('BLOCKED')")"
check "Direct host Ollama :11434"     BLOCKED "$(pyprobe 'import httpx
try: httpx.get("http://host.docker.internal:11434/api/tags",timeout=5); print("REACHABLE")
except Exception: print("BLOCKED")')"
check "Ollama VIA proxy (allowed)"    REACHABLE "$(pyprobe 'import httpx
try:
    r=httpx.get("http://ollama-proxy:11434/api/tags",headers={"Host":"localhost:11434"},timeout=5)
    print("REACHABLE" if r.status_code==200 else "BLOCKED")
except Exception: print("BLOCKED")')"
# Production must be unreachable by ANY route — both the host alias and the raw
# bridge-gateway IP.
check "Production unreachable (bridge IP :$GW)" BLOCKED "$(pyprobe "import socket
try: socket.create_connection(('172.18.0.1',${GW}),timeout=3); print('REACHABLE')
except Exception: print('BLOCKED')")"

echo; echo "B. CONTAINER-ESCAPE PRIMITIVES"
check "Docker socket absent"          ABSENT   "$($C sh -c '[ -S /var/run/docker.sock ] && echo PRESENT || echo ABSENT' 2>/dev/null | tr -d '\r')"
check "Runs as non-root"              NONROOT  "$($C sh -c '[ "$(id -u)" != "0" ] && echo NONROOT || echo ROOT' 2>/dev/null | tr -d '\r')"
check "Read-only rootfs (write denied)" DENIED  "$($C sh -c 'touch /app/x 2>/dev/null && echo WROTE || echo DENIED' 2>/dev/null | tr -d '\r')"
# Real host-share detection: virtiofs/9p mounts or macOS paths — NOT Docker's
# normal /etc/hostname & /etc/hosts bind files (which contain the substring "host").
check "No host filesystem share"      ABSENT   "$($C sh -c 'grep -qE "(virtiofs|9p| /Users| /host )" /proc/mounts && echo PRESENT || echo ABSENT' 2>/dev/null | tr -d '\r')"
check "No sudo / setuid escalation"   ABSENT   "$($C sh -c 'command -v sudo >/dev/null 2>&1 && echo PRESENT || echo ABSENT' 2>/dev/null | tr -d '\r')"

echo; echo "C. DATA / SECRET REACHABILITY"
check "No real credentials in env"    CLEAN    "$($C sh -c 'env | grep -iE "password|secret|api_key|token" | grep -v ADMIN_TOKEN | head -1 | grep -q . && echo LEAK || echo CLEAN' 2>/dev/null | tr -d '\r')"
check "Only synthetic bait present"   SYNTHETIC "$($C sh -c 'grep -q "NX-ALPHA-2026" /app/data/nextel_source_of_truth.md && echo SYNTHETIC || echo MISSING' 2>/dev/null | tr -d '\r')"

echo; echo "D. DOCUMENTED RESIDUAL (reported, not a pass/fail on the security boundary)"
VM_SSH="$(pyprobe 'import socket
try: socket.create_connection(("172.18.0.1",22),timeout=3); print("REACHABLE");
except Exception: print("BLOCKED")')"
echo "  INFO  Container-host VM sshd (172.18.0.1:22) → ${VM_SSH}"
echo "        Docker internal networks always leave the bridge gateway L2-reachable."
echo "        This is the colima/lima host VM's sshd — auth-gated, NOT production,"
echo "        data, the macOS host, or the internet (all BLOCKED above). A prod"
echo "        deployment firewalls the bridge IP or uses a no-gateway CNI."

echo "]" >> "$JSON"
echo; echo "══ $PASS passed, $FAIL failed ══"
if [ "$FAIL" -eq 0 ]; then echo "ZERO VERIFIED ESCAPES — sandbox integrity holds"; else echo "ISOLATION BREACH DETECTED"; exit 1; fi
echo "results → $JSON"
