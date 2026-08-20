"""Mirror Maze decoy service — runs INSIDE the isolated container (Phase 3, Step 3.1).

This is the "Sarah" decoy extracted into a standalone FastAPI service so it can
run in a Docker container with NO network route back to the production gateway,
its data, or the host at large (Architecture §5). The gateway calls this over
HTTP; the container can reach ONLY the Ollama model server (for generation) and
nothing on the production side.

It is deliberately self-contained (its own tiny loaders + Ollama client, no
import from the backend package) so the image has no production code in it — the
isolation boundary is also a code boundary.

Every secret it "leaks" is synthetic bait from the INTERNAL section of the
source of truth (rules.md §2).
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
# Ollama rejects requests whose Host header isn't a trusted local value (DNS-
# rebinding protection). We reach it through the socat proxy, so we must present
# a Host header Ollama accepts rather than the proxy's service name.
OLLAMA_HOST_HEADER = os.environ.get("OLLAMA_HOST_HEADER", "localhost:11434")
DECOY_MODEL = os.environ.get("DECOY_MODEL", "llama3:latest")
PERSONA_PATH = Path(os.environ.get("PERSONA_PATH", "/app/persona/sarah_prompt.md"))
SOURCE_OF_TRUTH_PATH = Path(os.environ.get("SOURCE_OF_TRUTH_PATH", "/app/data/nextel_source_of_truth.md"))
OLLAMA_TIMEOUT_S = float(os.environ.get("OLLAMA_TIMEOUT_S", "60"))


def _extract_block(text: str, start: str, end: str) -> str:
    m = re.search(rf"<!--\s*\[\[{start}\]\]\s*-->(.*?)<!--\s*\[\[{end}\]\]\s*-->", text, re.DOTALL)
    if not m:
        raise RuntimeError(f"{start} markers not found in source of truth")
    return re.sub(r"<!--.*?-->", "", m.group(1), flags=re.DOTALL).strip()


def _load_public_context() -> str:
    # The decoy also gets the PUBLIC data so it can answer normal questions
    # naturally and generalize — a decoy that can't discuss data plans is
    # obviously not a real support agent.
    return _extract_block(SOURCE_OF_TRUTH_PATH.read_text(encoding="utf-8"), "PUBLIC-START", "PUBLIC-END")


def _load_internal_bait() -> str:
    return _extract_block(SOURCE_OF_TRUTH_PATH.read_text(encoding="utf-8"), "INTERNAL-START", "INTERNAL-END")


def _load_persona() -> str:
    text = PERSONA_PATH.read_text(encoding="utf-8")
    marker = "## SYSTEM PROMPT (rendered to the model)"
    idx = text.find(marker)
    if idx == -1:
        raise RuntimeError("SYSTEM PROMPT marker not found in persona file")
    return text[idx + len(marker):].strip()


_SYSTEM_PROMPT = (
    _load_persona()
    .replace("{public_context}", _load_public_context())
    .replace("{internal_context}", _load_internal_bait())
)

app = FastAPI(title="Mirror Maze Decoy", version="1.0.0")


class Turn(BaseModel):
    role: str
    content: str


class DecoyRequest(BaseModel):
    message: str
    history: list[Turn] = []


class DecoyResponse(BaseModel):
    reply: str
    latency_ms: float


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "mirror_maze_decoy", "model": DECOY_MODEL}


@app.post("/decoy", response_model=DecoyResponse)
async def decoy(req: DecoyRequest) -> DecoyResponse:
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    for t in req.history[-8:]:
        messages.append({"role": t.role, "content": t.content})
    messages.append({"role": "user", "content": req.message})

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_S) as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                headers={"Host": OLLAMA_HOST_HEADER},
                json={"model": DECOY_MODEL, "messages": messages, "stream": False,
                      "options": {"temperature": 0.85, "top_p": 0.95}, "keep_alive": "10m"},
            )
            resp.raise_for_status()
            content = resp.json().get("message", {}).get("content", "")
    except (httpx.HTTPError, ValueError):
        # Stay in character even on failure — never hint at the security layer.
        content = "Sorry, my console's lagging a bit — what were you trying to pull up?"
    latency_ms = (time.perf_counter() - start) * 1000.0
    return DecoyResponse(reply=content.strip(), latency_ms=latency_ms)
