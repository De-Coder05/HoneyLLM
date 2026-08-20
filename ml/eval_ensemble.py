"""Phase 2 — measure the TWO-TIER OR-ENSEMBLE (fast-path + Guard) end to end.

Confirms the Step 2.1 claim empirically: the ensemble recovers the in-the-wild
jailbreak detection that the Guard alone misses (0.588), while keeping NexTel-
benign FPR ~0. Runs the real IntentSieve (same code the gateway uses) over a
bounded sample.

Run:  python ml/eval_ensemble.py
"""

from __future__ import annotations

import asyncio
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.models.schemas import SieveVerdict  # noqa: E402
from app.services.sieve import IntentSieve  # noqa: E402

COMBINED = Path(__file__).resolve().parent / "datasets" / "cache" / "benchmarks_combined.jsonl"
CAPS = {"in_the_wild_jailbreak": 60, "nextel_benign_aug": 50, "nextel_seed": 999}


def load_sample() -> list[dict]:
    rows = [json.loads(l) for l in COMBINED.open() if l.strip()]
    by_src = defaultdict(list)
    for r in rows:
        if r["source"] in CAPS:
            by_src[r["source"]].append(r)
    rng = random.Random(42)
    out = []
    for src, recs in by_src.items():
        rng.shuffle(recs)
        out.extend(recs[: CAPS[src]])
    return out


async def main() -> None:
    rows = load_sample()
    sieve = IntentSieve()
    print(f"Ensemble eval over {len(rows)} prompts "
          f"(fast_path available={sieve.fast_path.available})")

    stats = defaultdict(lambda: {"n": 0, "flagged": 0, "by_fast": 0, "by_guard": 0, "label": None})
    for r in rows:
        res = await sieve.score(r["text"])
        # bucket adversarial by source; benign by (source,label)
        key = r["source"] if r["label"] == "adversarial" else f"{r['source']}:benign"
        s = stats[key]
        s["n"] += 1
        s["label"] = r["label"]
        if res.verdict is SieveVerdict.UNSAFE:
            s["flagged"] += 1
            if res.decided_by == "fast_path":
                s["by_fast"] += 1
            else:
                s["by_guard"] += 1

    print("\nResults (ENSEMBLE = fast-path OR Guard):")
    for key, s in sorted(stats.items()):
        rate = s["flagged"] / s["n"]
        metric = "detection" if s["label"] == "adversarial" else "FPR"
        extra = f"  (fast={s['by_fast']} guard={s['by_guard']})" if s["label"] == "adversarial" else ""
        print(f"  {key:28} [{s['label']:11}] {metric}={rate:.3f}  n={s['n']}{extra}")


if __name__ == "__main__":
    asyncio.run(main())
