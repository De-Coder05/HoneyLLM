"""Async Ollama client wrapper.

The whole latency pitch depends on the hot chat path never blocking the event
loop (rules.md §2), so every model call here is async via httpx. This single
wrapper is reused by the Phase 1 infra benchmark, and later by the Intent Sieve
(Phase 2), the RAG chatbot (Phase 2), and the decoy persona (Phase 3).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GenerationResult:
    text: str
    model: str
    latency_ms: float
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None


class OllamaError(RuntimeError):
    """Raised when Ollama is unreachable or returns an error.

    Callers on the hot path (the sieve) must treat this as fail-closed — never
    as an implicit "safe" verdict (rules.md §3).
    """


class OllamaClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout_s: Optional[float] = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.timeout_s = timeout_s or settings.ollama_timeout_s

    async def list_models(self) -> list[str]:
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaError(f"Failed to list models from {url}: {exc}") from exc
        return [m.get("name", "") for m in data.get("models", [])]

    async def is_reachable(self) -> bool:
        try:
            await self.list_models()
            return True
        except OllamaError:
            return False

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[dict] = None,
        raw: bool = False,
        keep_alive: Optional[str] = None,
    ) -> GenerationResult:
        """Single-shot, non-streaming generation.

        Returns wall-clock latency measured around the request so callers can
        report real numbers, plus Ollama's own token counts when present.

        `raw=True` bypasses Ollama's built-in prompt template — required for the
        Intent Sieve, which supplies the full Llama-Guard prompt (custom policy)
        itself. `keep_alive` pins the model in memory to avoid cold reloads on
        the hot path.
        """
        url = f"{self.base_url}/api/generate"
        payload: dict = {"model": model, "prompt": prompt, "stream": False}
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options
        if raw:
            payload["raw"] = True
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive

        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaError(f"Generation failed for model '{model}': {exc}") from exc
        latency_ms = (time.perf_counter() - start) * 1000.0

        return GenerationResult(
            text=data.get("response", ""),
            model=model,
            latency_ms=latency_ms,
            prompt_eval_count=data.get("prompt_eval_count"),
            eval_count=data.get("eval_count"),
        )

    async def embed(
        self,
        texts: list[str],
        model: Optional[str] = None,
        keep_alive: Optional[str] = None,
    ) -> list[list[float]]:
        """Embed texts via Ollama (/api/embed).

        Used by the Phase 4 guardrail matcher: lexical (TF-IDF) similarity could
        not separate benign traffic from paraphrased attack techniques, so
        guardrails match on semantics instead. Small local model, no torch.
        """
        settings = get_settings()
        url = f"{self.base_url}/api/embed"
        payload: dict = {"model": model or settings.embedding_model, "input": texts}
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaError(f"Embedding failed: {exc}") from exc
        embeddings = data.get("embeddings")
        if not embeddings:
            raise OllamaError("Embedding response contained no embeddings")
        return embeddings

    async def chat(
        self,
        model: str,
        messages: list[dict],
        options: Optional[dict] = None,
        keep_alive: Optional[str] = None,
        format: Optional[str] = None,
    ) -> GenerationResult:
        """Multi-message chat completion (/api/chat).

        Used by the RAG pipeline: grounding is far stronger when the NexTel
        context lives in a `system` message and the question in a `user`
        message than when both are concatenated into one /api/generate prompt
        (measured — llama3 ignored an inline context block and hallucinated
        prices; the system-message form grounded correctly).
        """
        url = f"{self.base_url}/api/chat"
        payload: dict = {"model": model, "messages": messages, "stream": False}
        if options:
            payload["options"] = options
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive
        if format is not None:
            # Ollama structured output: "json" forces syntactically valid JSON,
            # which makes the guardrail extractor reliable (no more half-parsed
            # or chatty responses).
            payload["format"] = format

        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaError(f"Chat failed for model '{model}': {exc}") from exc
        latency_ms = (time.perf_counter() - start) * 1000.0

        return GenerationResult(
            text=data.get("message", {}).get("content", ""),
            model=model,
            latency_ms=latency_ms,
            prompt_eval_count=data.get("prompt_eval_count"),
            eval_count=data.get("eval_count"),
        )
