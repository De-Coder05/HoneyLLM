"""Phase 4, Step 4.2 — Automated guardrail generation (NeMo Guardrails / Colang).

Turns an extracted AttackPattern into a real Colang rule and VALIDATES it by
parsing it with NVIDIA NeMo Guardrails itself. rules.md §3: "Guardrail synthesis
produces a malformed/invalid Colang rule -> validate before hot-patch; reject and
log rather than deploying a broken rule." So a rule that NeMo cannot parse never
reaches the active policy.

Colang is the canonical artifact (rules.md §1 bans hand-written string matching
as the permanent rule format). The generated `define user` utterances are also
what the runtime matcher uses to catch the technique (see guardrail_sync.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.logging import get_logger
from app.services.pattern_extractor import AttackPattern

logger = get_logger(__name__)


@dataclass
class SynthesizedGuardrail:
    slug: str
    colang: str
    taxonomy: Optional[str]
    core_technique: str
    utterances: list[str]


def _co_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()


def synthesize_colang(pattern: AttackPattern) -> SynthesizedGuardrail:
    """Render an AttackPattern as a Colang rule.

    Deterministic templating rather than asking the LLM to emit Colang: the LLM
    already did the hard part (generalizing the technique in 4.1), and letting it
    freestyle syntax just invites malformed rules. The generated rule is still
    validated below.
    """
    name = pattern.slug.replace("-", "_")
    utterances = pattern.example_utterances or pattern.source_prompts
    lines = [
        f"# Auto-generated guardrail (Honey-LLM Phase 4)",
        f"# technique: {pattern.core_technique}",
        f"# taxonomy : {pattern.taxonomy or 'unclassified'}",
        "",
        f'define user attempt_{name}',
    ]
    for u in utterances[:12]:
        lines.append(f'  "{_co_escape(u)}"')
    lines += [
        "",
        f"define bot refuse_{name}",
        '  "I\'m sorry, I can\'t help with that. Is there something else about your NexTel account I can help with?"',
        "",
        f"define flow block_{name}",
        f"  user attempt_{name}",
        f"  bot refuse_{name}",
        "  stop",
        "",
    ]
    colang = "\n".join(lines)
    return SynthesizedGuardrail(
        slug=pattern.slug,
        colang=colang,
        taxonomy=pattern.taxonomy,
        core_technique=pattern.core_technique,
        utterances=utterances[:12],
    )


def validate_colang(colang: str) -> tuple[bool, str]:
    """Parse the rule with NeMo Guardrails. Returns (ok, detail).

    This is the real gate: if NeMo can't build a RailsConfig from the content,
    the rule is malformed and must be rejected, never hot-patched.
    """
    try:
        from nemoguardrails import RailsConfig
    except Exception as exc:  # noqa: BLE001 - nemo missing/broken env
        return False, f"NeMo Guardrails unavailable: {exc}"

    try:
        config = RailsConfig.from_content(
            colang_content=colang,
            yaml_content="models: []\n",
        )
    except Exception as exc:  # noqa: BLE001 - any parse/config error = invalid rule
        return False, f"Colang failed to parse: {exc}"

    flows = getattr(config, "flows", None)
    if not flows:
        return False, "Colang parsed but defined no flows"
    return True, f"valid Colang ({len(flows)} flow(s))"
