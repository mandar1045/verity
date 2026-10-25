// Offline mock API backed by fixtures recorded from the real backend
// (scripts/export_fixtures.py). Fixtures load lazily, so live mode never ships them.
// Unknown messages fall back to a neutral result.
import type {
  AnalyzeMessageRequest,
  DemoUser,
  FeedItem,
  Health,
  Lang,
  MessageAnalysis,
  Metrics,
  QuizItem,
  SampleMessage,
  TxnAnalysis,
} from "@contracts/types";

interface Fixtures {
  samples: SampleMessage[];
  quiz: QuizItem[];
  users: DemoUser[];
  analyses: Record<string, Record<Lang, MessageAnalysis>>;
  feeds: Record<string, Record<Lang, FeedItem[]>>;
  metrics: Metrics;
}

let cache: Promise<Fixtures> | null = null;
const load = (): Promise<Fixtures> =>
  (cache ??= import("./fixtures/fixtures.json").then((m) => m.default as unknown as Fixtures));

async function serve<T>(pick: (f: Fixtures) => T, ms = 250): Promise<T> {
  const value = pick(await load());
  await new Promise((resolve) => window.setTimeout(resolve, ms));
  return value;
}

function neutral(): MessageAnalysis {
  return {
    id: crypto.randomUUID(),
    risk_score: 12,
    label: "SAFE",
    scam_type: null,
    model_prob: 0.12,
    rule_score: 0,
    signals: [],
    links: [],
    explanation: "Offline demo mode: this message is not in the recorded set. Start the backend for a live analysis.",
    next_steps: ["Start the Verity backend (make dev) to analyse new messages."],
    explanation_source: "template",
  };
}

export const mockApi = {
  health: () => Promise.resolve<Health>({ status: "ok", models_loaded: true }),
  sampleMessages: () => serve((f) => f.samples),
  quiz: () => serve((f) => f.quiz),
  analyzeMessage: (req: AnalyzeMessageRequest) =>
    serve((f) => {
      const hit = f.analyses[req.text.trim()];
      return hit ? { ...hit[req.lang_out], id: crypto.randomUUID() } : neutral();
    }, 450),
  demoUsers: () => serve((f): DemoUser[] => f.users),
  feed: (userId: string, lang: Lang, limit = 50) => serve((f) => (f.feeds[userId]?.[lang] ?? []).slice(0, limit)),
  analyzeTransaction: (req: { transaction: { txn_id: string; user_id: string }; lang_out: Lang }) =>
    serve((f): TxnAnalysis => {
      const item = f.feeds[req.transaction.user_id]?.[req.lang_out]?.find((x) => x.transaction.txn_id === req.transaction.txn_id);
      if (!item) throw new Error("Transaction not in offline fixtures.");
      return item.analysis;
    }),
  feedback: () => Promise.resolve({ ok: true as const }),
  metrics: () => serve((f): Metrics => f.metrics),
};
