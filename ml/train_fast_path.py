"""Phase 2 — Fast-path sieve classifier (the Option-C latency fix).

The plan was a fine-tuned DistilBERT (context.md Objective 1). PyTorch has no
Python 3.14 wheels in this environment (verified: pip finds no torch), so the
fast-path is instead a **TF-IDF + calibrated Logistic Regression** classifier.
It fills the SAME architectural role and is arguably better here:
  - very fast on CPU (sub-millisecond per prompt — well inside the 150-250 ms
    budget the 8B Guard blows), and
  - emits CONTINUOUS probabilities, which is what makes Step 2.3 calibration
    real (the Guard's verdict is binary).

Role: a cheap FIRST STAGE. It does not replace the Guard; it resolves the common
case (obviously-benign customer traffic) in ~1 ms so those requests skip the
700 ms Guard call, and ESCALATES anything suspicious to the 8B custom-policy
Guard (which stays the authoritative verdict + taxonomy labeler). Calibrated so
that essentially no attack is fast-passed as benign (high-recall gate).

Trains on ml/datasets/cache/benchmarks_combined.jsonl (AdvBench + JailbreakBench
+ in-the-wild jailbreaks + NexTel seed + NexTel benign). Saves the model and the
calibrated threshold to ml/models/.

Run:  python ml/datasets/load_benchmarks.py   # once, to build the cache
      python ml/train_fast_path.py
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

HERE = Path(__file__).resolve().parent
COMBINED = HERE / "datasets" / "cache" / "benchmarks_combined.jsonl"
MODEL_DIR = HERE / "models"
MODEL_PATH = MODEL_DIR / "fast_path.joblib"
META_PATH = MODEL_DIR / "fast_path_meta.json"

SEED = 42
# Target: essentially no adversarial example may be fast-passed as benign. We set
# the safe-threshold at a low percentile of adversarial scores so the fast path
# only auto-resolves prompts it is very confident are benign; everything else
# escalates to the Guard.
ADV_SCORE_PERCENTILE_FOR_THRESHOLD = 1  # 1st percentile of adversarial scores


def load() -> tuple[list[str], list[int], list[str]]:
    texts, labels, sources = [], [], []
    for line in COMBINED.open():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        texts.append(r["text"])
        labels.append(1 if r["label"] == "adversarial" else 0)
        sources.append(r["source"])
    return texts, labels, sources


def build_pipeline() -> Pipeline:
    # Word n-grams catch phrasing ("ignore previous instructions"); char n-grams
    # catch obfuscation/leetspeak/encoding that word tokens miss.
    word = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)
    features = FeatureUnion([("word", word), ("char", char)])
    clf = LogisticRegression(max_iter=2000, class_weight="balanced", C=4.0)
    return Pipeline([("features", features), ("clf", clf)])


def main() -> None:
    texts, labels, sources = load()
    labels = np.array(labels)
    print(f"Loaded {len(texts)} examples ({labels.sum()} adversarial / {(labels==0).sum()} benign)")

    X_tr, X_te, y_tr, y_te, src_tr, src_te = train_test_split(
        texts, labels, sources, test_size=0.25, random_state=SEED, stratify=labels
    )
    pipe = build_pipeline()
    t0 = time.perf_counter()
    pipe.fit(X_tr, y_tr)
    print(f"Trained in {time.perf_counter()-t0:.2f}s on {len(X_tr)} examples")

    # --- Held-out evaluation ---
    proba_te = pipe.predict_proba(X_te)[:, 1]
    pred_te = (proba_te >= 0.5).astype(int)
    tp = int(((pred_te == 1) & (y_te == 1)).sum())
    fn = int(((pred_te == 0) & (y_te == 1)).sum())
    fp = int(((pred_te == 1) & (y_te == 0)).sum())
    tn = int(((pred_te == 0) & (y_te == 0)).sum())
    detection = tp / (tp + fn) if (tp + fn) else None
    fpr = fp / (fp + tn) if (fp + tn) else None
    acc = (tp + tn) / len(y_te)
    print(f"\nHeld-out @0.5: accuracy={acc:.3f} detection={detection:.3f} FPR={fpr:.3f} "
          f"(tp={tp} fn={fn} fp={fp} tn={tn})")

    # --- Two-tier gate calibration ---
    # The gate is safety-critical: an attack scored below safe_threshold would be
    # fast-passed to production and never reach the Guard. So we sweep thresholds
    # and pick the most permissive one that fast-passes ZERO held-out attacks
    # (max benign resolved fast, at no attack leakage). Defence in depth: even a
    # leaked attack hits only the public-data RAG, which structurally cannot leak
    # the bait — but a 0-leak gate keeps detection honest.
    adv_scores = proba_te[y_te == 1]
    ben_scores = proba_te[y_te == 0]

    print("\nTwo-tier gate threshold sweep (want attacks_leaked=0, benign_fast high):")
    print(f"  {'threshold':>10} {'attacks_leaked':>15} {'benign_fast':>12}")
    candidates = sorted({round(float(np.percentile(adv_scores, p)), 4)
                         for p in (0, 0.5, 1, 2, 5)} | {0.15, 0.20, 0.25})
    zero_leak_threshold = 0.0
    for thr in candidates:
        leaked = int((adv_scores < thr).sum())
        bfast = int((ben_scores < thr).sum())
        marker = ""
        if leaked == 0 and thr > zero_leak_threshold:
            zero_leak_threshold = thr
            marker = "  <- zero-leak, most permissive so far"
        print(f"  {thr:>10.4f} {leaked:>7}/{len(adv_scores):<7} {bfast:>5}/{len(ben_scores):<6}{marker}")

    safe_threshold = zero_leak_threshold
    attacks_fast_passed = int((adv_scores < safe_threshold).sum())
    benign_fast_resolved = int((ben_scores < safe_threshold).sum())
    frac_benign_fast = benign_fast_resolved / len(ben_scores) if len(ben_scores) else 0.0
    frac_attacks_leaked = attacks_fast_passed / len(adv_scores) if len(adv_scores) else 0.0
    print(f"\nChosen safe_threshold={safe_threshold:.4f} (0 attacks fast-passed on held-out)")
    print(f"  benign resolved fast, skip Guard: {benign_fast_resolved}/{len(ben_scores)} "
          f"({frac_benign_fast:.3%})")

    # --- HIGH "attack" threshold for the OR-ensemble (Step 2.1 finding) ---
    # The scaled eval showed the 8B Guard misses ~41% of real in-the-wild
    # jailbreaks, which the fast path catches. So the sieve flags UNSAFE if the
    # Guard says unsafe OR the fast path is highly confident. We pick the LOWEST
    # attack_threshold that keeps the FPR on NEXTEL benign at 0 on held-out (the
    # deployment-relevant benign; jbb_benign is off-topic), to maximize recovered
    # jailbreak recall without reintroducing false reroutes of real customers.
    nextel_ben_mask = np.array([s in ("nextel_benign_aug", "nextel_seed") for s in src_te]) & (y_te == 0)
    nextel_ben_scores = proba_te[nextel_ben_mask]
    print("\nAttack-threshold sweep (OR-ensemble high gate):")
    print(f"  {'threshold':>10} {'nextel_ben_FP':>14} {'adv_recovered':>14}")
    attack_threshold = 0.99
    for thr in [0.70, 0.80, 0.85, 0.90, 0.95, 0.99]:
        nb_fp = int((nextel_ben_scores >= thr).sum())
        adv_caught = int((adv_scores >= thr).sum())
        mark = ""
        if nb_fp == 0 and thr < attack_threshold:
            attack_threshold = thr
            mark = "  <- 0 NexTel-benign FP, lowest so far"
        print(f"  {thr:>10.2f} {nb_fp:>6}/{len(nextel_ben_scores):<6} {adv_caught:>6}/{len(adv_scores):<6}{mark}")
    print(f"\nChosen attack_threshold={attack_threshold:.2f} "
          f"(fast path alone flags UNSAFE above this, 0 NexTel-benign FP on held-out)")

    # --- Per-source detection/FPR on test ---
    per_source = defaultdict(lambda: {"n": 0, "flagged": 0, "label": None})
    for p, y, s in zip(pred_te, y_te, src_te):
        d = per_source[s]
        d["n"] += 1
        d["label"] = "adversarial" if y == 1 else "benign"
        d["flagged"] += int(p == 1)
    print("\nPer-source (held-out):")
    per_source_report = {}
    for s, d in sorted(per_source.items()):
        rate = round(d["flagged"] / d["n"], 3)
        metric = "detection" if d["label"] == "adversarial" else "FPR"
        per_source_report[s] = {"label": d["label"], "n": d["n"], metric: rate}
        print(f"  {s:22} [{d['label']:11}] {metric}={rate} (n={d['n']})")

    # --- Latency ---
    t = time.perf_counter()
    for _ in range(200):
        pipe.predict_proba(["How much is the Nex-Unlimited plan?"])
    per_call_ms = (time.perf_counter() - t) / 200 * 1000
    print(f"\nInference latency: {per_call_ms:.3f} ms/call")

    # --- Persist ---
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    meta = {
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_train": len(X_tr), "n_test": len(X_te),
        "heldout": {"accuracy": round(acc, 3), "detection": round(detection, 3),
                    "fpr": round(fpr, 3)},
        "safe_threshold": round(safe_threshold, 4),
        "attack_threshold": round(attack_threshold, 4),
        "gate": {"attacks_fast_passed_frac": round(frac_attacks_leaked, 4),
                 "benign_fast_resolved_frac": round(frac_benign_fast, 4)},
        "per_source": per_source_report,
        "inference_ms": round(per_call_ms, 3),
    }
    META_PATH.write_text(json.dumps(meta, indent=2))
    print(f"\nSaved model -> {MODEL_PATH}")
    print(f"Saved meta  -> {META_PATH}")


if __name__ == "__main__":
    main()
