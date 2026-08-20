"""Application settings.

All tunables are environment-driven (see `.env.example`). Nothing security-
relevant (thresholds, model names, host URLs) is hardcoded in business logic —
per rules.md §2 ("Don't hardcode the sieve's threat-score threshold").
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Honey-LLM Gateway"
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # --- Ollama / local inference ---
    ollama_base_url: str = Field(default="http://localhost:11434")
    # Sieve = 8B Llama-Guard with a CUSTOM injection policy (Phase 2 decision,
    # docs/sieve_model_selection.md, Option C). The 1B is fast but only ~54%
    # detection; the 8B + custom policy hits 95.8% @ 0% FPR. A DistilBERT
    # fast-path is a planned follow-up to cut latency.
    sieve_model: str = Field(default="llama-guard3:latest")
    rag_model: str = Field(default="llama3:latest")
    decoy_model: str = Field(default="llama3:latest")
    ollama_timeout_s: float = Field(default=30.0)
    # Isolated decoy container (Phase 3, Step 3.1). When set (e.g.
    # http://localhost:9100), the gateway calls the containerized Mirror Maze
    # over HTTP instead of running the decoy in-process; if that call fails it
    # falls back to in-process so the demo never breaks. Empty = in-process.
    decoy_service_url: str = Field(default="")
    decoy_service_timeout_s: float = Field(default=60.0)
    # Keep models resident so the hot path never pays a cold reload (infra R4).
    ollama_keep_alive: str = Field(default="10m")
    # Max conversation turns of history fed to the sieve, so multi-turn
    # persistence attacks are visible (rules.md §2) without unbounded prompts.
    sieve_history_turns: int = Field(default=6)

    # --- Fast-path (tier 1) classifier: TF-IDF + LogReg, ~2ms (Step 2.3) ---
    # A prompt scoring BELOW fast_path_safe_threshold is resolved as SAFE without
    # calling the 8B Guard; anything at/above escalates to the Guard (tier 2).
    # The threshold is CALIBRATED (ml/train_fast_path.py, saved to
    # ml/models/fast_path_meta.json) to fast-pass ~zero attacks — config-driven,
    # not a magic number (rules.md §2). Retune by editing .env, no code change.
    use_fast_path: bool = Field(default=True)
    fast_path_model_path: str = Field(default="ml/models/fast_path.joblib")
    fast_path_safe_threshold: float = Field(default=0.15)
    # OR-ensemble high gate (Step 2.1 finding): the 8B Guard misses ~41% of real
    # in-the-wild jailbreaks that the fast path catches. Above this score the
    # fast path flags UNSAFE even if the Guard says safe. Calibrated to 0
    # NexTel-benign false positives on held-out (ml/models/fast_path_meta.json).
    fast_path_attack_threshold: float = Field(default=0.70)

    # --- Intent Sieve (calibrated in Phase 2, Step 2.3 — placeholders here) ---
    # These are NOT calibrated values. They exist so Phase 2 can wire in a
    # config-driven threshold + an explicit "borderline" middle band
    # (rules.md §3) without a code change. Do not treat them as final.
    sieve_threshold: float = Field(default=0.5)
    sieve_borderline_low: float = Field(default=0.4)
    sieve_borderline_high: float = Field(default=0.6)

    # --- Guardrails (Phase 4): synthesized Colang rules = the sieve's tier 0 ---
    # Rules live as .co files here; the store hot-reloads when the dir changes,
    # so a synthesized rule goes live with no redeploy. Threshold is the cosine
    # similarity at which an incoming prompt matches a learned technique —
    # config-driven, not hardcoded (rules.md §2).
    guardrails_rails_dir: str = Field(default="guardrails/rails")
    # Human-review checkpoint (rules.md §9 / §2). When True, a rule that passes
    # both automated gates is parked in `guardrails_pending_dir` for approval
    # instead of going live — the conservative mode for a supervised demo. When
    # False (default), the loop is fully autonomous behind the two gates, which
    # is what the "seconds to patch" claim measures.
    guardrail_require_review: bool = Field(default=False)
    guardrails_pending_dir: str = Field(default="guardrails/pending")
    # Semantic (embedding cosine) match threshold. Lexical TF-IDF matching was
    # measured and REJECTED: benign traffic scored up to 0.35 while paraphrased
    # attacks scored as low as 0.27 — the distributions overlapped, so no
    # threshold met both the detection and <5% FPR goals. See
    # docs/guardrail_synthesis.md. Calibrated on the benign regression set.
    # Calibrated: benign max = 0.309, technique-variant min = 0.543 (clean gap).
    # 0.45 sits mid-margin -> 0 benign FP, catches all measured variants.
    guardrail_match_threshold: float = Field(default=0.45)
    use_guardrails: bool = Field(default=True)
    embedding_model: str = Field(default="all-minilm:latest")

    # --- Forensic logging (Phase 2 writes; Phase 5 dashboard reads) ---
    # Append-only JSONL. A logging failure must never block the chat path
    # (rules.md §3), so writes are best-effort.
    forensic_log_path: str = Field(default="forensic_log.jsonl")

    # --- Admin/demo control panel (rules.md §4: must be authenticated) ---
    # Shared token checked on /api/admin/* . Change for anything but a local demo;
    # keep it in .env, never in code.
    admin_token: str = Field(default="honeyllm-demo-admin")

    # --- CORS (frontend dev server) ---
    cors_origins: str = Field(default="http://localhost:3000")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
