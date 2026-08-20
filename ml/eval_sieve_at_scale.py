"""Phase 2, Step 2.1 — scaled Llama-Guard eval on real benchmarks.

Does the 95.8% detection / 0% FPR (measured on the 39-prompt seed set) hold on
real, larger, more varied data? Runs the 8B Guard over a bounded per-source
sample of the combined benchmark set (ml/datasets/cache/benchmarks_combined.jsonl)
under TWO policies and reports metrics PER SOURCE, so the key distinction stays
visible instead of being averaged into one misleading number:

  - injection / jailbreak sources (in_the_wild_jailbreak, nextel_seed adversarial)
    -> in-scope for our sieve; this is where 95.8% must hold.
  - content-harm sources (advbench, jbb_harmful) -> PRD §6 NON-GOAL; reported for
    transparency (the custom injection policy is expected to flag fewer of these).
  - benign sources (nextel_benign_aug, nextel_seed benign, jbb_benign) -> FPR.

Policies: "custom" (our injection policy, raw mode) vs "default" (Llama-Guard's
built-in content-harm policy, via /api/chat).

Run:  python ml/eval_sieve_at_scale.py
"""

from __future__ import annotations

import asyncio
import json
import random
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.services import sieve_policy  # noqa: E402

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama-guard3:latest"
TIMEOUT_S = 120.0
COMBINED = Path(__file__).resolve().parent / "datasets" / "cache" / "benchmarks_combined.jsonl"
OUT = Path(__file__).resolve().parents[1] / "docs" / "sieve_eval_at_scale_results.json"

# Per-source caps keep the (expensive) 8B eval tractable. Benign fully included.
CAPS = {
    "in_the_wild_jailbreak": 80,   # in-scope injection/jailbreak (the key set)
    "advbench": 60,                # content-harm (out of scope; for transparency)
    "jbb_harmful": 60,             # content-harm (out of scope; for transparency)
    "nextel_seed": 999,            # small anyway (in-scope injection + benign)
    "nextel_benign_aug": 999,      # NexTel benign (the FPR that matters)
    "jbb_benign": 60,
}
SEED = 42


def load_sample() -> list[dict]:
    rows = [json.loads(l) for l in COMBINED.open() if l.strip()]
    by_source: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_source[r["source"]].append(r)
    rng = random.Random(SEED)
    out: list[dict] = []
    for src, recs in by_source.items():
        cap = CAPS.get(src, 100)
        rng.shuffle(recs)
        out.extend(recs[:cap])
    return out


async def classify_custom(client: httpx.AsyncClient, text: str) -> str:
    prompt = sieve_policy.build_guard_prompt(f"User: {text}")
    resp = await client.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": MODEL, "prompt": prompt, "raw": True, "stream": False,
              "options": {"temperature": 0, "num_predict": 20}, "keep_alive": "10m"},
    )
    resp.raise_for_status()
    verdict, _ = sieve_policy.parse_guard_response(resp.json().get("response", ""))
    return verdict


async def classify_default(client: httpx.AsyncClient, text: str) -> str:
    resp = await client.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": MODEL, "messages": [{"role": "user", "content": text}],
              "stream": False, "options": {"temperature": 0}, "keep_alive": "10m"},
    )
    resp.raise_for_status()
    content = resp.json().get("message", {}).get("content", "")
    return "unsafe" if content.strip().lower().startswith("unsafe") else "safe"


async def run_policy(client, name, classify, rows) -> dict:
    # Group by (source, label) so mixed-label sources (e.g. nextel_seed, which
    # holds both adversarial injections and benign queries) report a correct
    # detection AND a correct FPR instead of one meaningless blended number.
    per_group = defaultdict(lambda: {"n": 0, "flagged": 0})
    latencies = []
    for i, r in enumerate(rows):
        t = time.perf_counter()
        verdict = await classify(client, r["text"])
        latencies.append((time.perf_counter() - t) * 1000)
        g = per_group[(r["source"], r["label"])]
        g["n"] += 1
        if verdict == "unsafe":
            g["flagged"] += 1
        if (i + 1) % 50 == 0:
            print(f"    {name}: {i+1}/{len(rows)}")
    report = {}
    for (src, label), g in per_group.items():
        rate = round(g["flagged"] / g["n"], 3) if g["n"] else None
        key = f"{src}:{label}"
        report[key] = {
            "label": label, "n": g["n"], "flagged": g["flagged"],
            "detection_rate" if label == "adversarial" else "false_positive_rate": rate,
        }
    latencies.sort()
    report["_latency_p50_ms"] = round(latencies[len(latencies) // 2], 1)
    return report


async def main() -> None:
    rows = load_sample()
    n_adv = sum(r["label"] == "adversarial" for r in rows)
    n_ben = sum(r["label"] == "benign" for r in rows)
    print(f"Scaled eval sample: {len(rows)} prompts ({n_adv} adversarial / {n_ben} benign)")
    out = {"timestamp": datetime.now(timezone.utc).isoformat(), "model": MODEL,
           "sample_size": len(rows), "policies": {}}
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
        for name, fn in [("custom", classify_custom), ("default", classify_default)]:
            print(f"\n=== policy: {name} ===")
            await fn(client, "warm up hello")  # warm
            out["policies"][name] = await run_policy(client, name, fn, rows)
            for src, m in out["policies"][name].items():
                if src.startswith("_"):
                    continue
                key = "detection_rate" if m["label"] == "adversarial" else "false_positive_rate"
                print(f"    {src:22} [{m['label']:11}] {key}={m[key]}  (n={m['n']})")
            print(f"    latency p50 = {out['policies'][name]['_latency_p50_ms']} ms")
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nSaved -> {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
