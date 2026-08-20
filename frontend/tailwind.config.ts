import type { Config } from "tailwindcss";

/**
 * Design tokens are the single source of truth shared with the Stitch design
 * system ("NexTel System") and design.md. Three surfaces (chat / dashboard /
 * admin) are themed from ONE config via namespaced tokens — never three
 * separate design systems (design.md §4).
 */
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // --- NexTel chat widget (light, trust-forward telecom) — design.md §1 ---
        nextel: {
          primary: "#0B5FFF",
          secondary: "#00B8A9",
          surface: "#FFFFFF",
          bg: "#F4F6F8",
          bot: "#F1F3F5",
          botText: "#101418",
          border: "#E2E5E9",
          muted: "#6B7280",
          success: "#0CA30C",
        },
        // --- Dashboard / admin (dark SOC) — design.md §2/§3 (used from Phase 5) ---
        soc: {
          plane: "#0d0d0d",
          card: "#1a1a19",
          ink: "#ffffff",
          ink2: "#c3c2b7",
          muted: "#898781",
          grid: "#2c2c2a",
          axis: "#383835",
          good: "#0ca30c",
          warning: "#fab219",
          serious: "#ec835a",
          critical: "#d03b3b",
          honey: "#E8A93A", // admin-panel-only accent (design.md §3)
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        mono: ["ui-monospace", "SF Mono", "Cascadia Code", "monospace"],
      },
      borderRadius: {
        bubble: "1rem",
      },
    },
  },
  plugins: [],
};

export default config;
