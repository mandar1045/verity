// Typed API client. All shapes come from contracts/types.ts.
// VITE_USE_MOCKS=true serves recorded fixtures so the demo runs fully offline.
import type {
  AnalyzeMessageRequest,
  AnalyzeTransactionRequest,
  DemoUser,
  FeedbackRequest,
  FeedbackResponse,
  FeedItem,
  Health,
  Lang,
  MessageAnalysis,
  Metrics,
  QuizItem,
  SampleMessage,
  TxnAnalysis,
} from "@contracts/types";
import { mockApi } from "./mocks";

const BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ?? "http://localhost:8000";
export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true";
const TIMEOUT_MS = 12_000;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(`${BASE}/api/v1${path}`, {
      ...init,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    });
    if (!res.ok) {
      const body: unknown = await res.json().catch(() => null);
      const detail = body && typeof body === "object" && "detail" in body ? String((body as { detail: unknown }).detail) : res.statusText;
      throw new ApiError(detail || `Request failed (${res.status})`, res.status);
    }
    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    const aborted = err instanceof DOMException && err.name === "AbortError";
    throw new ApiError(aborted ? "The server took too long to answer." : "Cannot reach the Verity server.", 0);
  } finally {
    window.clearTimeout(timer);
  }
}

const post = <T>(path: string, body: unknown) => request<T>(path, { method: "POST", body: JSON.stringify(body) });

const liveApi = {
  health: () => request<Health>("/health"),
  sampleMessages: () => request<SampleMessage[]>("/samples/messages"),
  quiz: () => request<QuizItem[]>("/samples/quiz"),
  analyzeMessage: (req: AnalyzeMessageRequest) => post<MessageAnalysis>("/analyze/message", req),
  demoUsers: () => request<DemoUser[]>("/transactions/demo-users"),
  feed: (userId: string, lang: Lang, limit = 50) =>
    request<FeedItem[]>(`/transactions/feed?user_id=${encodeURIComponent(userId)}&limit=${limit}&lang_out=${lang}`),
  analyzeTransaction: (req: AnalyzeTransactionRequest) => post<TxnAnalysis>("/analyze/transaction", req),
  feedback: (req: FeedbackRequest) => post<FeedbackResponse>("/feedback", req),
  metrics: () => request<Metrics>("/metrics"),
};

export type Api = typeof liveApi;
export const api: Api = USE_MOCKS ? mockApi : liveApi;
