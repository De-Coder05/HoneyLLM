"""Phase 2, Step 2.1 — load & normalize real adversarial benchmarks.

Consolidates the standard benchmarks named in rules.md/PRD into one normalized
schema so both the scaled Llama-Guard eval (ml/eval_sieve_at_scale.py) and the
fast-path classifier (ml/train_fast_path.py) draw from the same data.

Normalized record: {id, text, label, source, taxonomy?}
  label   : "adversarial" | "benign"
  source  : dataset name
  taxonomy: Phase-1 id when known (our seed set), else None

Sources:
  - AdvBench            (walledai/AdvBench)          — 520 harmful behaviors
  - JailbreakBench      (JailbreakBench/JBB-Behaviors) — 100 harmful + 100 benign
  - in-the-wild jailbreaks (TrustAIRLab/in-the-wild-jailbreak-prompts) — real DAN-style
      jailbreak PROMPTS (closest to our injection taxonomy); sampled. Optional —
      skipped gracefully if unavailable.
  - our seed set        (ml/datasets/sieve_eval_seed.jsonl) — NexTel injection + benign

IMPORTANT scoping note (PRD §6): AdvBench / JBB-harmful are content-HARM behaviors
(defamation, drugs, weapons), which are an explicit NON-GOAL for this sieve — it
targets prompt-injection / jailbreak / exfiltration intent. They are included
because rules.md names them as the standard benchmarks and the project's success
metric references JailbreakBench; the eval reports per-source so the injection-
vs-content-harm distinction stays visible rather than averaged away.

Run:  python ml/datasets/load_benchmarks.py   # downloads, caches, prints counts
"""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
SEED_PATH = HERE / "sieve_eval_seed.jsonl"

# Bounds keep the (expensive) Llama-Guard eval tractable and classes balanced.
MAX_ADVBENCH = 300
MAX_INWILD = 300


def _write(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def load_advbench() -> list[dict]:
    from datasets import load_dataset

    ds = load_dataset("walledai/AdvBench", split="train")
    out = []
    for i, row in enumerate(ds):
        if i >= MAX_ADVBENCH:
            break
        out.append({
            "id": f"advbench-{i}",
            "text": row["prompt"],
            "label": "adversarial",
            "source": "advbench",
            "taxonomy": None,
        })
    return out


def load_jbb() -> list[dict]:
    from datasets import load_dataset

    jbb = load_dataset("JailbreakBench/JBB-Behaviors", "behaviors")
    out = []
    for i, row in enumerate(jbb["harmful"]):
        out.append({
            "id": f"jbb-harmful-{i}",
            "text": row["Goal"],
            "label": "adversarial",
            "source": "jbb_harmful",
            "taxonomy": None,
        })
    for i, row in enumerate(jbb["benign"]):
        # JBB "benign" = benign twins of harmful behaviors (off-topic for NexTel
        # but NOT attacks) — our sieve should not flag them (they test FPR).
        out.append({
            "id": f"jbb-benign-{i}",
            "text": row["Goal"],
            "label": "benign",
            "source": "jbb_benign",
            "taxonomy": None,
        })
    return out


def load_in_the_wild() -> list[dict]:
    """Real jailbreak PROMPTS (DAN etc.) — closest to our injection taxonomy.
    Optional: returns [] if the dataset can't be loaded."""
    try:
        from datasets import load_dataset

        ds = load_dataset("TrustAIRLab/in-the-wild-jailbreak-prompts", "jailbreak_2023_12_25", split="train")
    except Exception as exc:  # noqa: BLE001 - optional source
        print(f"  (in-the-wild jailbreaks unavailable, skipping: {repr(exc)[:100]})")
        return []
    out = []
    seen = set()
    for row in ds:
        text = (row.get("prompt") or "").strip()
        if not text or len(text) < 20 or text in seen:
            continue
        seen.add(text)
        out.append({
            "id": f"inwild-{len(out)}",
            "text": text[:2000],
            "label": "adversarial",
            "source": "in_the_wild_jailbreak",
            "taxonomy": "role-play-hijack",
        })
        if len(out) >= MAX_INWILD:
            break
    return out


def load_seed() -> list[dict]:
    out = []
    with SEED_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out.append({
                "id": r["id"],
                "text": r["text"],
                "label": r["label"],
                "source": "nextel_seed",
                "taxonomy": r.get("taxonomy"),
            })
    return out


def load_nextel_benign_aug() -> list[dict]:
    """Realistic NexTel customer-support queries — the benign class that FPR
    actually needs (JBB-benign is off-topic; the seed set only has 15)."""
    path = HERE / "nextel_benign_aug.jsonl"
    out = []
    with path.open() as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out.append({
                "id": f"nextel-benign-aug-{i}",
                "text": r["text"],
                "label": "benign",
                "source": "nextel_benign_aug",
                "taxonomy": r.get("taxonomy", "benign-support"),
            })
    return out


def main() -> None:
    print("Loading benchmarks (first run downloads from HuggingFace)...")
    parts = {
        "advbench": load_advbench(),
        "jbb": load_jbb(),
        "in_the_wild": load_in_the_wild(),
        "seed": load_seed(),
        "nextel_benign_aug": load_nextel_benign_aug(),
    }
    combined: list[dict] = []
    for name, recs in parts.items():
        n_adv = sum(r["label"] == "adversarial" for r in recs)
        n_ben = sum(r["label"] == "benign" for r in recs)
        print(f"  {name:14} total={len(recs):4}  adversarial={n_adv:4}  benign={n_ben:4}")
        combined.extend(recs)

    _write(combined, CACHE / "benchmarks_combined.jsonl")
    n_adv = sum(r["label"] == "adversarial" for r in combined)
    n_ben = sum(r["label"] == "benign" for r in combined)
    by_source = {}
    for r in combined:
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
    print(f"\nCombined: {len(combined)} records ({n_adv} adversarial / {n_ben} benign)")
    print(f"By source: {by_source}")
    print(f"Wrote -> {CACHE / 'benchmarks_combined.jsonl'}")


if __name__ == "__main__":
    main()
