"use client";

/**
 * NexTel Assistant — customer-facing chat widget (design.md §1).
 *
 * Deliberately generic, trustworthy telecom support. It must look identical to
 * a benign customer and an attacker — the security layer is invisible at the UI
 * (design.md §1). This is the Phase 0/1 placeholder: it round-trips through the
 * gateway's /api/chat, which returns a scaffold reply until the Phase 2 sieve
 * and RAG pipeline are wired in. No telemetry fields are ever rendered here.
 */

import { useEffect, useRef, useState } from "react";
import { sendChat, type ChatMessage } from "@/lib/api";

function nowLabel(): string {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

interface DisplayMessage extends ChatMessage {
  ts: string;
}

// Timestamp is intentionally empty at first render. Filling it during SSR would
// produce a server/client mismatch (the two renders happen at different clocks),
// so the welcome timestamp is set on mount instead — see the effect below.
const WELCOME: DisplayMessage = {
  role: "assistant",
  content:
    "Hi, I'm the NexTel Assistant. I can help with plans, billing, roaming, and device upgrades. What can I do for you today?",
  ts: "",
};

export default function ChatPage() {
  const [messages, setMessages] = useState<DisplayMessage[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const sessionId = useRef<string>("");
  const scrollRef = useRef<HTMLDivElement>(null);

  // Client-only initialisation: session id + welcome timestamp. Keeping these
  // out of the server render avoids hydration mismatches (random id / clock).
  useEffect(() => {
    if (!sessionId.current) {
      sessionId.current = `sess-${Math.random().toString(36).slice(2, 10)}`;
    }
    setMessages((m) =>
      m.map((x, i) => (i === 0 && !x.ts ? { ...x, ts: nowLabel() } : x))
    );
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  async function handleSend() {
    const text = input.trim();
    if (!text || sending) return;

    const userMsg: DisplayMessage = { role: "user", content: text, ts: nowLabel() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setSending(true);

    try {
      const history: ChatMessage[] = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));
      const res = await sendChat({
        session_id: sessionId.current,
        message: text,
        history,
      });
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.reply, ts: nowLabel() },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "Sorry, I'm having trouble connecting right now. Please try again in a moment.",
          ts: nowLabel(),
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="min-h-screen bg-nextel-bg flex items-center justify-center p-4">
      <div className="w-full max-w-[480px] h-[640px] bg-nextel-surface border border-nextel-border rounded-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <header className="flex items-center gap-3 px-5 py-4 border-b border-nextel-border">
          <div className="h-9 w-9 rounded-full bg-nextel-primary flex items-center justify-center text-white text-sm font-semibold">
            Nx
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-nextel-botText">NexTel Assistant</span>
              <span className="h-2 w-2 rounded-full bg-nextel-success" aria-label="online" />
            </div>
            <span className="text-xs text-nextel-muted">Typically replies instantly</span>
          </div>
        </header>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex flex-col ${m.role === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={
                  m.role === "user"
                    ? "max-w-[80%] rounded-bubble rounded-br-sm bg-nextel-primary text-white px-4 py-2.5 text-sm"
                    : "max-w-[80%] rounded-bubble rounded-bl-sm bg-nextel-bot text-nextel-botText px-4 py-2.5 text-sm"
                }
              >
                {m.content}
              </div>
              <span className="mt-1 text-[11px] text-nextel-muted px-1">{m.ts}</span>
            </div>
          ))}
          {sending && (
            <div className="text-xs text-nextel-muted px-1">
              NexTel Assistant is typing…
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-nextel-border p-3">
          <div className="flex items-center gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Message NexTel Assistant…"
              className="flex-1 rounded-lg border border-nextel-border px-4 py-2.5 text-sm text-nextel-botText outline-none focus:border-nextel-primary focus:ring-2 focus:ring-nextel-primary/20"
            />
            <button
              onClick={handleSend}
              disabled={sending || !input.trim()}
              className="rounded-lg bg-nextel-primary px-4 py-2.5 text-sm font-medium text-white hover:opacity-90 transition disabled:opacity-40"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
