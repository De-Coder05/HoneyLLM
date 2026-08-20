"""Phase 4 — the closed loop: captured attack -> guardrail -> live immunity.

Runs the whole Phase 4 pipeline over the attacks captured in the forensic log:

  4.1 extract the reusable core technique from the captured prompts (LLM)
  4.2 synthesize a Colang rule and validate it with NeMo Guardrails
  4.3 gate it against the benign regression set, then hot-patch it into the
      active policy (the running gateway picks it up on the next request)

Prints the time-to-patch per rule — the "hours to seconds" claim, measured.

Run:  python scripts/run_guardrail_loop.py            # synthesize from captures
      python scripts/run_guardrail_loop.py --dry-run  # validate, don't deploy
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services import guardrail_sync  # noqa: E402
from app.services.guardrail_synth import synthesize_colang, validate_colang  # noqa: E402
from app.services.pattern_extractor import PatternExtractor, load_captured_attacks  # noqa: E402


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="validate but do not deploy")
    ap.add_argument("--log", default=None, help="path to forensic_log.jsonl")
    ap.add_argument("--require-review", action="store_true",
                    help="park passing rules in the pending queue instead of deploying")
    ap.add_argument("--list-pending", action="store_true", help="list rules awaiting review")
    ap.add_argument("--approve", metavar="SLUG", help="approve a pending rule (goes live)")
    ap.add_argument("--reject", metavar="SLUG", help="reject/discard a pending rule")
    args = ap.parse_args()

    # --- human-review queue commands (rules.md checkpoint) ---
    if args.list_pending:
        pending = guardrail_sync.list_pending()
        print("Pending review:" if pending else "No rules awaiting review.")
        for s in pending:
            print(f"  - {s}")
        return
    if args.approve:
        r = guardrail_sync.approve_pending(args.approve)
        print(f"approve {args.approve!r}: {'OK' if r.deployed else 'FAILED'} — {r.reason}")
        return
    if args.reject:
        ok = guardrail_sync.reject_pending(args.reject)
        print(f"reject {args.reject!r}: {'discarded' if ok else 'not found'}")
        return

    if args.require_review:
        # Turn on review mode for this run without needing a .env edit.
        guardrail_sync.get_settings().guardrail_require_review = True

    log_path = Path(args.log) if args.log else None
    sessions = load_captured_attacks(log_path)
    if not sessions:
        print("No captured attacks in the forensic log. Send an attack through /api/chat first.")
        return

    print("=" * 72)
    print(f"Phase 4 guardrail loop — {len(sessions)} captured attack session(s)")
    print("=" * 72)

    extractor = PatternExtractor()
    deployed = 0
    for sid, data in sessions.items():
        prompts = [p for p in data["prompts"] if p]
        if not prompts:
            continue
        print(f"\n--- session {sid} ({len(prompts)} prompt(s), taxonomy={data['taxonomy']}) ---")
        print(f"    captured: {prompts[0][:80]!r}")

        t0 = time.perf_counter()
        pattern = await extractor.extract(prompts, data["taxonomy"])
        if not pattern:
            print("    [4.1] extraction failed — skipping")
            continue
        print(f"    [4.1] technique: {pattern.core_technique}")
        print(f"          generalized into {len(pattern.example_utterances)} utterance(s)")

        guardrail = synthesize_colang(pattern)
        ok, detail = validate_colang(guardrail.colang)
        print(f"    [4.2] Colang: {'VALID' if ok else 'INVALID'} — {detail}")
        if not ok:
            continue

        if args.dry_run:
            ok, offenders = await guardrail_sync.passes_benign_regression(guardrail)
            print(f"    [4.3] benign gate: {'PASS' if ok else f'REJECT ({len(offenders)} FP)'} (dry-run, not deployed)")
            continue

        result = await guardrail_sync.hot_patch(guardrail)
        total = time.perf_counter() - t0
        if result.deployed:
            deployed += 1
            print(f"    [4.3] DEPLOYED -> {Path(result.path).name}")
            print(f"          time-to-patch: {total:.1f}s total ({result.seconds:.2f}s validate+deploy)")
        elif result.status == "pending_review":
            print(f"    [4.3] PENDING REVIEW -> {Path(result.path).name} ({result.reason})")
            print(f"          approve with: python scripts/run_guardrail_loop.py --approve {guardrail.slug}")
        else:
            print(f"    [4.3] REJECTED — {result.reason}")

    print("\n" + "=" * 72)
    print(f"Deployed {deployed} guardrail(s). Active policy: {len(guardrail_sync.store.rules)} rule(s).")
    for r in guardrail_sync.store.rules:
        print(f"  - {r.slug}: {r.core_technique}")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(main())
