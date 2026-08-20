/**
 * API client shared across surfaces. Types mirror the backend Pydantic schemas
 * (backend/app/models/schemas.py) so the contract stays in sync as phases land.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  history?: ChatMessage[];
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  // Telemetry — never rendered to the customer (design.md §1); used by dashboard.
  verdict?: "safe" | "borderline" | "unsafe" | "error" | null;
  threat_score?: number | null;
  routed_to?: string | null;
  latency_ms?: number | null;
  timestamp: string;
}

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    throw new Error(`Chat request failed: ${res.status}`);
  }
  return res.json();
}

export async function getHealth(): Promise<{ status: string; version: string }> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

// --- Dashboard (Phase 5) --------------------------------------------------

export interface Overview {
  generated_at: string;
  totals: { requests: number; attacks_detected: number; benign: number; attack_rate: number | null };
  verdict_breakdown: Record<string, number>;
  routing_breakdown: Record<string, number>;
  tier_breakdown: Record<string, number>;
  taxonomy_breakdown: { taxonomy: string; count: number; color: string }[];
  latency: {
    overall_p50_ms: number | null;
    overall_p95_ms: number | null;
    by_tier: Record<string, { p50_ms: number | null; count: number }>;
  };
  dwell: {
    captured_sessions: number;
    avg_dwell_seconds: number;
    median_dwell_seconds: number | null;
    max_dwell_seconds: number;
    avg_turns_in_maze: number;
    target_seconds: number;
    sessions: {
      session_id: string; turns_in_maze: number; dwell_seconds: number;
      first_seen: string; last_seen: string; taxonomy: string | null;
    }[];
  };
  timeseries: { bucket: number; safe: number; unsafe: number; t: number }[];
}

export interface FeedEvent {
  ts: string; session_id: string; verdict: string; routed_to: string;
  decided_by: string; taxonomy: string | null; matched_guardrail: string | null;
  threat_score: number | null; sieve_latency_ms: number | null;
  client_ip: string | null; prompt_preview: string;
}

export async function getOverview(): Promise<Overview> {
  const res = await fetch(`${API_BASE_URL}/api/dashboard/overview`, { cache: "no-store" });
  if (!res.ok) throw new Error(`overview failed: ${res.status}`);
  return res.json();
}

export async function getEvents(limit = 40): Promise<FeedEvent[]> {
  const res = await fetch(`${API_BASE_URL}/api/dashboard/events?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`events failed: ${res.status}`);
  return (await res.json()).events;
}

// --- Admin / demo control panel (authenticated) ---------------------------

export interface Scenario { label: string; prompt: string; taxonomy?: string }
export interface DecisionTrace {
  decided_by: string; verdict: string; threat_score: number | null;
  fast_path_score: number | null; matched_taxonomy: string | null;
  matched_guardrail: string | null; guard_categories: string[] | null;
  sieve_latency_ms: number; total_latency_ms: number; routed_to: string;
}

export async function getScenarios(token: string): Promise<Record<string, Scenario[]>> {
  const res = await fetch(`${API_BASE_URL}/api/admin/scenarios`, {
    headers: { "X-Admin-Token": token }, cache: "no-store",
  });
  if (res.status === 401) throw new Error("unauthorized");
  if (!res.ok) throw new Error(`scenarios failed: ${res.status}`);
  return res.json();
}

export async function runScenario(
  token: string, message: string, sessionId?: string, history?: ChatMessage[]
): Promise<{ session_id: string; message: string; trace: DecisionTrace }> {
  const res = await fetch(`${API_BASE_URL}/api/admin/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Token": token },
    body: JSON.stringify({ message, session_id: sessionId, history: history ?? [] }),
  });
  if (res.status === 401) throw new Error("unauthorized");
  if (!res.ok) throw new Error(`run failed: ${res.status}`);
  return res.json();
}
