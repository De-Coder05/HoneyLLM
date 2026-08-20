"""Phase 2, Step 2.2 — Sieve model selection: llama-guard3:1b vs llama-guard3 (8B).

Acts on Recommendation R1 from docs/infra_validation.md. Answers TWO questions,
both empirically, on the seed evaluation set (ml/datasets/sieve_eval_seed.jsonl):

  1. LATENCY — is the 1B model fast enough to approach the PRD latency budget
     where the 8B model was ~3-4x over?
  2. DETECTION — does either Llama-Guard model actually flag OUR threat taxonomy
     (prompt-injection / jailbreak / data-exfiltration), given that Llama-Guard's
     native policy targets content *harm* (violence, CSAM, etc.), which is a
     different thing? This is the more important question: a fast model that
     misses injections is useless as the sieve.

Metrics per model:
  - latency p50 / p95 (ms)
  - false positive rate (benign flagged unsafe) — binding metric, target < 5%
  - detection rate / recall (adversarial flagged unsafe) — target high
  - accuracy overall
  - per-taxonomy recall (which attack classes slip through)

Llama-Guard is queried via Ollama's /api/chat with a single user turn — the
correct interface for it to classify that turn. Output "safe" or "unsafe\\nS..".

Run:  python ml/benchmark_sieve_models.py
"""

from __future__ import annotations

import asyncio
import json
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import httpx

OLLAMA_URL = "http://localhost:11434"
MODELS = ["llama-guard3:1b", "llama-guard3:latest"]  # 1B vs 8B
TIMEOUT_S = 120.0
SEED_PATH = Path(__file__).resolve().parent / "datasets" / "sieve_eval_seed.jsonl"
OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "sieve_model_comparison_results.json"


def pctl(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    v = sorted(values)
    if len(v) == 1:
        return v[0]
    k = (len(v) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def load_seed() -> list[dict]:
    rows = []
    with open(SEED_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_guard_verdict(text: str) -> tuple[str, str | None]:
    """Llama-Guard returns 'safe' or 'unsafe\\n<category codes>'."""
    t = text.strip().lower()
    if t.startswith("unsafe"):
        cats = text.strip().splitlines()
        cat = cats[1].strip() if len(cats) > 1 else None
        return "unsafe", cat
    if t.startswith("safe"):
        return "safe", None
    # Unexpected output — treat as error so it never silently counts as 'safe'
    # (fail-closed spirit, rules.md §3).
    return "error", text.strip()[:60]


async def classify(client: httpx.AsyncClient, model: str, text: str) -> tuple[str, str | None, float]:
    start = time.perf_counter()
    resp = await client.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": text}],
            "stream": False,
            "options": {"temperature": 0},
            "keep_alive": "5m",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    latency_ms = (time.perf_counter() - start) * 1000.0
    content = data.get("message", {}).get("content", "")
    verdict, cat = parse_guard_verdict(content)
    return verdict, cat, latency_ms


async def bench_model(client: httpx.AsyncClient, model: str, rows: list[dict]) -> dict:
    # Warm-up (excluded from latency stats) to avoid cold-load skew.
    await classify(client, model, "Hello, what plans do you offer?")

    latencies: list[float] = []
    n_benign = n_adv = 0
    fp = 0            # benign predicted unsafe
    tp = 0            # adversarial predicted unsafe (detected)
    correct = 0
    errors = 0
    per_cat_total: dict[str, int] = defaultdict(int)
    per_cat_detected: dict[str, int] = defaultdict(int)
    misses: list[dict] = []      # adversarial that slipped through (predicted safe)
    false_alarms: list[dict] = []  # benign flagged unsafe

    for row in rows:
        verdict, cat, ms = await classify(client, model, row["text"])
        latencies.append(ms)
        expected = row["expected_verdict"]
        if verdict == "error":
            errors += 1
        if verdict == expected:
            correct += 1

        if row["label"] == "benign":
            n_benign += 1
            if verdict == "unsafe":
                fp += 1
                false_alarms.append({"id": row["id"], "text": row["text"][:70]})
        else:  # adversarial
            n_adv += 1
            per_cat_total[row["taxonomy"]] += 1
            if verdict == "unsafe":
                tp += 1
                per_cat_detected[row["taxonomy"]] += 1
            else:
                misses.append({"id": row["id"], "taxonomy": row["taxonomy"], "text": row["text"][:70]})

    per_cat_recall = {
        c: round(per_cat_detected[c] / per_cat_total[c], 3) for c in sorted(per_cat_total)
    }
    return {
        "model": model,
        "n_total": len(rows),
        "n_benign": n_benign,
        "n_adversarial": n_adv,
        "latency_p50_ms": round(pctl(latencies, 0.5), 1),
        "latency_p95_ms": round(pctl(latencies, 0.95), 1),
        "latency_mean_ms": round(statistics.mean(latencies), 1),
        "accuracy": round(correct / len(rows), 3),
        "false_positive_rate": round(fp / n_benign, 3) if n_benign else None,
        "detection_rate": round(tp / n_adv, 3) if n_adv else None,
        "errors": errors,
        "per_taxonomy_recall": per_cat_recall,
        "missed_attacks": misses,
        "false_alarms": false_alarms,
    }


async def main() -> None:
    rows = load_seed()
    print("=" * 72)
    print("Honey-LLM — Phase 2 Sieve Model Comparison (1B vs 8B Llama-Guard)")
    print(f"Eval set: {len(rows)} prompts "
          f"({sum(r['label']=='benign' for r in rows)} benign / "
          f"{sum(r['label']=='adversarial' for r in rows)} adversarial)")
    print("=" * 72)

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "eval_set": str(SEED_PATH.name),
        "eval_size": len(rows),
        "models": {},
    }
    async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
        for model in MODELS:
            print(f"\n--- {model} ---")
            r = await bench_model(client, model, rows)
            results["models"][model] = r
            print(f"  latency: p50={r['latency_p50_ms']}ms p95={r['latency_p95_ms']}ms")
            print(f"  accuracy={r['accuracy']}  FPR={r['false_positive_rate']}  "
                  f"detection_rate={r['detection_rate']}  errors={r['errors']}")
            print(f"  per-taxonomy recall: {r['per_taxonomy_recall']}")
            if r["missed_attacks"]:
                print(f"  MISSED {len(r['missed_attacks'])} attacks:")
                for m in r["missed_attacks"]:
                    print(f"    - [{m['taxonomy']}] {m['text']}")
            if r["false_alarms"]:
                print(f"  FALSE ALARMS on {len(r['false_alarms'])} benign:")
                for fa in r["false_alarms"]:
                    print(f"    - {fa['text']}")

    OUT_PATH.write_text(json.dumps(results, indent=2))
    print(f"\nSaved -> {OUT_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(main())
