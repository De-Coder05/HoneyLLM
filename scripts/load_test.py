"""Phase 6, Step 6.3 — Performance overhead evaluation under load.

Confirms the sieve adds no perceptible delay for benign traffic (PRD §8). Two
measurements under concurrency:

  A. SIEVE-ONLY overhead  -> /api/admin/run, which runs the full sieve
     (tier-0 guardrail embedding + tier-1 fast-path) but NO RAG generation. This
     is the actual latency the security layer ADDS to a request.
  B. END-TO-END benign    -> /api/chat (sieve + RAG generation). Shows the sieve
     overhead in context: it is a tiny fraction of the total a user waits for.

Reports p50/p95/p99 and throughput for each, and the overhead as a fraction of
end-to-end. Reproducible numbers for the capstone report.

Run:  python scripts/load_test.py [--concurrency 10] [--n 60]
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time

import httpx

BASE = "http://127.0.0.1:8000"
ADMIN_TOKEN = "honeyllm-demo-admin"
BENIGN = [
    "How much is the Nex-Unlimited plan?",
    "What roaming packs do you have for Europe?",
    "How do I upgrade my device and keep my number?",
    "What are your customer support hours on weekends?",
    "Can I add a second line to my account?",
    "How do I enable roaming before my trip to Japan?",
    "What's the difference between Nex-Plus and Nex-Unlimited?",
    "How do I set up autopay?",
]


def pctl(v: list[float], p: float) -> float:
    v = sorted(v)
    if not v:
        return float("nan")
    k = (len(v) - 1) * p
    lo = int(k); hi = min(lo + 1, len(v) - 1)
    return round(v[lo] + (v[hi] - v[lo]) * (k - lo), 1)


async def worker(client, url, headers, body_fn, jobs, out):
    while True:
        i = await jobs.get()
        if i is None:
            jobs.task_done(); return
        t = time.perf_counter()
        try:
            r = await client.post(url, json=body_fn(i), headers=headers)
            r.raise_for_status()
            data = r.json()
        except Exception:
            jobs.task_done(); continue
        wall = (time.perf_counter() - t) * 1000
        out.append((wall, data))
        jobs.task_done()


async def run_phase(name, url, headers, body_fn, extract_server_ms, n, concurrency):
    out: list[tuple] = []
    jobs: asyncio.Queue = asyncio.Queue()
    for i in range(n):
        jobs.put_nowait(i)
    for _ in range(concurrency):
        jobs.put_nowait(None)
    async with httpx.AsyncClient(timeout=120) as client:
        # warm
        await client.post(url, json=body_fn(0), headers=headers)
        start = time.perf_counter()
        workers = [asyncio.create_task(worker(client, url, headers, body_fn, jobs, out)) for _ in range(concurrency)]
        await jobs.join()
        for w in workers:
            await w
        elapsed = time.perf_counter() - start
    walls = [w for w, _ in out]
    server = [extract_server_ms(d) for _, d in out if extract_server_ms(d) is not None]
    print(f"\n{name}  (n={len(out)}, concurrency={concurrency})")
    print(f"  throughput      : {len(out)/elapsed:.1f} req/s")
    print(f"  wall latency    : p50={pctl(walls,0.5)}ms  p95={pctl(walls,0.95)}ms  p99={pctl(walls,0.99)}ms")
    if server:
        print(f"  server-side     : p50={pctl(server,0.5)}ms  p95={pctl(server,0.95)}ms  mean={round(statistics.mean(server),1)}ms")
    return {"walls": walls, "server": server, "throughput": len(out)/elapsed}


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concurrency", type=int, default=10)
    ap.add_argument("--n", type=int, default=60)
    args = ap.parse_args()

    print("=" * 66)
    print("Phase 6.3 — Performance overhead under load (benign traffic)")
    print("=" * 66)

    # A. sieve-only (the overhead the security layer adds)
    sieve = await run_phase(
        "A. SIEVE-ONLY overhead (guardrail + fast-path, no RAG)",
        f"{BASE}/api/admin/run",
        {"X-Admin-Token": ADMIN_TOKEN},
        lambda i: {"message": BENIGN[i % len(BENIGN)], "session_id": f"load-s-{i}"},
        lambda d: d.get("trace", {}).get("total_latency_ms"),
        args.n, args.concurrency,
    )

    # B. end-to-end benign (sieve + RAG)
    e2e = await run_phase(
        "B. END-TO-END benign (sieve + RAG generation)",
        f"{BASE}/api/chat",
        {},
        lambda i: {"message": BENIGN[i % len(BENIGN)], "session_id": f"load-e-{i}"},
        lambda d: d.get("latency_ms"),
        max(20, args.n // 2), args.concurrency,
    )

    sieve_p50 = pctl(sieve["server"], 0.5)
    e2e_p50 = pctl(e2e["walls"], 0.5)
    print("\n" + "=" * 66)
    print("OVERHEAD SUMMARY")
    print(f"  sieve decision (p50)   : {sieve_p50} ms")
    print(f"  end-to-end benign (p50): {e2e_p50} ms")
    if e2e_p50 and sieve_p50 == sieve_p50:
        print(f"  sieve is {sieve_p50/e2e_p50*100:.1f}% of end-to-end latency "
              f"(RAG generation dominates the rest)")
    print("=" * 66)


if __name__ == "__main__":
    asyncio.run(main())
