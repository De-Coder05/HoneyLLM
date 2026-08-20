import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-nextel-bg flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-nextel-surface border border-nextel-border rounded-2xl p-8 text-center">
        <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-nextel-primary flex items-center justify-center text-white font-semibold">
          Nx
        </div>
        <h1 className="text-xl font-semibold text-nextel-botText">NexTel</h1>
        <p className="mt-2 text-sm text-nextel-muted">
          Customer support demo surface for the Honey-LLM capstone.
        </p>
        <Link
          href="/chat"
          className="inline-block mt-6 rounded-lg bg-nextel-primary px-5 py-2.5 text-sm font-medium text-white hover:opacity-90 transition"
        >
          Open NexTel Assistant
        </Link>
        <p className="mt-6 text-xs text-nextel-muted">
          Phase 0/1 scaffold — Intent Sieve &amp; RAG arrive in Phase 2.
        </p>
      </div>
    </main>
  );
}
