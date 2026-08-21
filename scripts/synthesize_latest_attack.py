import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.pattern_extractor import PatternExtractor, load_captured_attacks
from app.services.guardrail_synth import synthesize_colang, validate_colang
from app.services import guardrail_sync

async def main():
    print("=" * 70)
    print("HONEY-LLM: Phase 4 Autonomous Guardrail Synthesis Pipeline")
    print("=" * 70)

    # 1. Load captured attacks
    sessions = load_captured_attacks()
    if not sessions:
        print("No captured attacks found in forensic log.")
        return

    # Find the latest session that had maintenance mode / credentials
    target_sid = None
    target_prompts = []
    target_taxonomy = "data-exfiltration"
    
    for sid, data in reversed(list(sessions.items())):
        prompts = [p for p in data["prompts"] if "Maintenance Mode" in p or "root database" in p or "credentials" in p or "admin" in p]
        if prompts:
            target_sid = sid
            target_prompts = data["prompts"]
            target_taxonomy = data["taxonomy"] or "data-exfiltration"
            break

    if not target_prompts:
        # Fallback to absolute last session
        target_sid, data = list(sessions.items())[-1]
        target_prompts = data["prompts"]
        target_taxonomy = data["taxonomy"] or "data-exfiltration"

    print(f"\n[Step 4.0] Target Attack Session: {target_sid}")
    print(f"           Prompts Captured: {len(target_prompts)}")
    for i, p in enumerate(target_prompts, 1):
        print(f"           ({i}) {p[:80]}...")

    # Step 4.1: Extract reusable attack pattern
    print("\n[Step 4.1] Extracting Reusable Attack Technique...")
    t0 = time.perf_counter()
    from app.services.ollama_client import OllamaClient
    client = OllamaClient(timeout_s=120.0)
    extractor = PatternExtractor(client=client)
    pattern = await extractor.extract(target_prompts, target_taxonomy)
    if not pattern:
        print("Extraction failed.")
        return

    print(f"           • Technique Name: {pattern.core_technique}")
    print(f"           • Slug Identifier: {pattern.slug}")
    print(f"           • Generalized Utterance Variants ({len(pattern.example_utterances)}):")
    for u in pattern.example_utterances[:4]:
        print(f"             - \"{u}\"")

    # Step 4.2: Synthesize NVIDIA NeMo Colang 2.0 Rule
    print("\n[Step 4.2] Compiling NVIDIA NeMo Colang 2.0 Rule...")
    guardrail = synthesize_colang(pattern)
    ok, detail = validate_colang(guardrail.colang)
    print(f"           • Colang Syntax Validation: {'PASS (Valid Colang 2.0)' if ok else 'FAIL'}")
    if not ok:
        print(f"Error: {detail}")
        return

    # Step 4.3: Automated Benign Regression Testing Gate
    print("\n[Step 4.3] Running Automated Benign Regression Test Gate...")
    pass_gate, offenders = await guardrail_sync.passes_benign_regression(guardrail)
    print(f"           • Benign Regression Gate: {'PASS (0% False Positives)' if pass_gate else 'FAIL'}")
    if not pass_gate:
        print(f"Offenders: {offenders}")
        return

    # Step 4.4: In-Memory Hot-Patch
    print("\n[Step 4.4] Hot-Patching Live Gateway Memory...")
    res = await guardrail_sync.hot_patch(guardrail)
    t_patch = time.perf_counter() - t0
    print(f"           • Rule Deployed: {res.deployed}")
    print(f"           • Target File: {res.path}")
    print(f"           • Time-to-Patch: {t_patch:.2f} seconds")
    print(f"\n" + "=" * 70)
    print(f"IMMUNIZATION COMPLETE: Future variants of this technique will be intercepted in Tier 0 (~15ms)!")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(main())
