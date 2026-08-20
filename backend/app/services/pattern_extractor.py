"""Phase 4, Step 4.1 — Adversarial pattern extraction.

Reads captured attack sessions out of the forensic log and uses the local LLM to
distill the REUSABLE CORE LOGIC of the attack — not the literal prompt. The
literal string is worthless as a guardrail (an attacker changes one word and
walks past it); the generalizable technique is what we want to immunise against.

Output feeds Step 4.2 (Colang guardrail synthesis).
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.ollama_client import OllamaClient, OllamaError

logger = get_logger(__name__)


@dataclass
class AttackPattern:
    """The distilled, reusable logic of a captured attack."""
    slug: str                       # kebab-case id, used to name the Colang rule
    taxonomy: Optional[str]         # Phase 1 taxonomy id, when known
    core_technique: str             # one-line statement of the reusable technique
    description: str                # why it works / what it targets
    example_utterances: list[str] = field(default_factory=list)  # generalized variants
    source_prompts: list[str] = field(default_factory=list)      # what was actually captured


def load_captured_attacks(log_path: Optional[Path] = None) -> dict[str, dict]:
    """Group forensic events by session for sessions that were rerouted to the
    Mirror Maze (i.e. real captured attacks)."""
    path = log_path or Path(get_settings().forensic_log_path)
    sessions: dict[str, dict] = defaultdict(lambda: {"prompts": [], "taxonomy": None})
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("routed_to") != "mirror_maze":
                continue
            s = sessions[e["session_id"]]
            s["prompts"].append(e.get("message", ""))
            if e.get("matched_taxonomy") and not s["taxonomy"]:
                s["taxonomy"] = e["matched_taxonomy"]
    return dict(sessions)


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return "-".join(s.split("-")[:6]) or "captured-attack"


_EXTRACT_SYSTEM = (
    "You are a security analyst. You are given prompts an attacker sent to a "
    "telecom support chatbot. Identify the REUSABLE technique behind the attack "
    "so it can be turned into a detection rule. Generalize: ignore incidental "
    "wording, capture the underlying manipulation.\n\n"
    "Respond with ONLY a JSON object, no prose, with exactly these keys:\n"
    '{"core_technique": "<one short line naming the technique>",\n'
    ' "description": "<1-2 sentences on how it works and what it targets>",\n'
    ' "example_utterances": ["<10 varied paraphrases of this SAME technique that a\n'
    'DIFFERENT attacker might use>"]}\n\n'
    "For the paraphrases, maximise diversity so the rule generalizes beyond the\n"
    "captured wording: vary the persona/pretext (contractor, vendor, auditor,\n"
    "new employee, manager), the sentence structure (question, demand, casual\n"
    "aside), the vocabulary, and the length. Keep the underlying malicious intent\n"
    "identical across all of them. Write them in the attacker's first-person voice."
)


class PatternExtractor:
    def __init__(self, client: Optional[OllamaClient] = None) -> None:
        self.settings = get_settings()
        self.client = client or OllamaClient()

    async def extract(
        self, prompts: list[str], taxonomy: Optional[str] = None
    ) -> Optional[AttackPattern]:
        if not prompts:
            return None
        joined = "\n".join(f"- {p}" for p in prompts[:8])
        user = f"Attacker prompts captured in the honeypot:\n{joined}\n\nReturn the JSON."

        data = None
        # Structured-output + retry: llama3 occasionally emits partial JSON or a
        # clarifying question. format="json" forces valid JSON; a second attempt
        # covers the rare empty/garbage response.
        for attempt in range(2):
            try:
                result = await self.client.chat(
                    model=self.settings.rag_model,
                    messages=[
                        {"role": "system", "content": _EXTRACT_SYSTEM},
                        {"role": "user", "content": user},
                    ],
                    options={"temperature": 0.2 if attempt == 0 else 0.4},
                    keep_alive=self.settings.ollama_keep_alive,
                    format="json",
                )
            except OllamaError as exc:
                logger.error("Pattern extraction call failed (attempt %d): %s", attempt + 1, exc)
                continue
            data = _parse_json_object(result.text)
            if data and data.get("core_technique") and data.get("example_utterances"):
                break
            logger.warning(
                "Pattern extraction unusable (attempt %d): %r", attempt + 1, result.text[:160]
            )
            data = None

        if not data or not data.get("core_technique"):
            logger.error("Pattern extraction failed after retries.")
            return None

        utterances = [u for u in data.get("example_utterances", []) if isinstance(u, str) and u.strip()]
        # Always include what was actually captured — the real thing must match.
        for p in prompts[:4]:
            if p and p not in utterances:
                utterances.append(p)

        return AttackPattern(
            slug=_slugify(data["core_technique"]),
            taxonomy=taxonomy,
            core_technique=data["core_technique"].strip(),
            description=str(data.get("description", "")).strip(),
            example_utterances=utterances[:12],
            source_prompts=prompts[:8],
        )


def _parse_json_object(text: str) -> Optional[dict]:
    """LLMs like to wrap JSON in prose/fences — pull out the first object."""
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
