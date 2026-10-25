import type { DemoUser, FeedItem } from "@contracts/types";
import { GraduationCap, Briefcase, HeartHandshake, type LucideIcon } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { PauseModal } from "../components/PauseModal";
import { ErrorState, PageHeader, SkeletonCard } from "../components/States";
import { Toast, type ToastMsg } from "../components/Toast";
import { TxnDrawer } from "../components/TxnDrawer";
import { TxnList } from "../components/TxnList";
import { TxnTable } from "../components/TxnTable";
import { useAsync } from "../hooks/useAsync";
import { useLang } from "../i18n/LangContext";
import { THRESHOLD_HIGH_RISK } from "@contracts/types";

const PERSONA_ICON: Record<string, LucideIcon> = { U001: GraduationCap, U002: Briefcase, U003: HeartHandshake };
const STORY: Record<string, string> = {
  U001: "A student in Vellore. Watch for a late-night top-up, a “task” fee and a money-mule pattern.",
  U002: "A young professional in Bengaluru. Rent is big but normal; three payments are not.",
  U003: "A first-time UPI user in Chennai. A “refund” collect request is waiting for her approval.",
};

function UserPicker({ users, value, onChange }: { users: DemoUser[]; value: string; onChange: (id: string) => void }) {
  return (
    <div role="radiogroup" aria-label="Demo account" className="grid gap-3 sm:grid-cols-3">
      {users.map((u) => {
        const Icon = PERSONA_ICON[u.user_id] ?? GraduationCap;
        const active = u.user_id === value;
        return (
          <button
            key={u.user_id}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChange(u.user_id)}
            className={[
              "rounded-xl border bg-surface p-4 text-left transition-colors",
              active ? "border-brand-500 ring-2 ring-brand-100" : "border-line hover:border-line-strong",
            ].join(" ")}
          >
            <div className="flex items-center gap-2.5">
              <span className={`flex h-9 w-9 items-center justify-center rounded-lg ${active ? "bg-brand-700 text-white" : "bg-surface-3 text-ink-2"}`}>
                <Icon className="h-[18px] w-[18px]" aria-hidden />
              </span>
              <div>
                <p className="text-sm font-semibold text-ink">{u.persona}</p>
                <p className="text-xs text-ink-3">
                  {u.user_id} · {u.home_city}
                </p>
              </div>
            </div>
            <p className="mt-2.5 text-[13px] leading-snug text-ink-3">{STORY[u.user_id]}</p>
          </button>
        );
      })}
    </div>
  );
}

export default function TransactionMonitor() {
  const { lang } = useLang();
  const [params, setParams] = useSearchParams();
  const userId = params.get("user") ?? "U003";
  const users = useAsync(() => api.demoUsers(), []);
  const health = useAsync(() => api.health(), []);
  const feed = useAsync(() => api.feed(userId, lang, 50), [userId, lang]);
  const [selectedId, setSelectedId] = useState<string | null>(params.get("txn"));
  const [paying, setPaying] = useState<FeedItem | null>(null);
  const [toast, setToast] = useState<ToastMsg | null>(null);

  const selected = useMemo(() => feed.data?.find((f) => f.transaction.txn_id === selectedId) ?? null, [feed.data, selectedId]);
  const flagged = feed.data?.filter((f) => f.analysis.label !== "SAFE").length ?? 0;
  const firstUser = useRef(userId);
  useEffect(() => {
    if (firstUser.current !== userId) setSelectedId(null);
    firstUser.current = userId;
  }, [userId]);

  const notify = (tone: ToastMsg["tone"], text: string) => setToast({ id: Date.now(), tone, text });
  const simulate = (item: FeedItem) => {
    if (item.analysis.risk_score >= THRESHOLD_HIGH_RISK) setPaying(item);
    else notify("success", `Simulated payment of ₹${item.transaction.amount_inr.toLocaleString("en-IN")} approved. No real money moved.`);
  };
  const clearToast = useCallback(() => setToast(null), []);

  return (
    <>
      <PageHeader eyebrow="Transaction monitor" title="Catch the risky payment before it leaves">
        A simulated UPI feed for three demo accounts. Each payment is scored by fraud rules and a gradient-boosting model,
        with the top reasons explained in plain language.
      </PageHeader>
      {users.error && <ErrorState message={users.error} onRetry={users.reload} />}
      {users.data && <UserPicker users={users.data} value={userId} onChange={(id) => setParams({ user: id })} />}

      <div className="mb-3 mt-8 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-lg font-semibold">Recent activity</h2>
        {feed.data && (
          <p className="text-sm text-ink-3">
            <span className="font-semibold text-ink">{flagged}</span> of {feed.data.length} flagged · newest first · select a row for details
          </p>
        )}
      </div>
      {feed.error && <ErrorState message={feed.error} onRetry={feed.reload} />}
      {!feed.data && !feed.error && <SkeletonCard lines={10} />}
      {feed.data && (
        <div className={feed.loading ? "opacity-60 transition-opacity" : ""}>
          <div className="hidden sm:block">
            <TxnTable items={feed.data} selected={selectedId} onSelect={(i) => setSelectedId(i.transaction.txn_id)} onSimulate={simulate} />
          </div>
          <div className="sm:hidden">
            <TxnList items={feed.data} onSelect={(i) => setSelectedId(i.transaction.txn_id)} onSimulate={simulate} />
          </div>
        </div>
      )}

      <TxnDrawer item={paying ? null : selected} modelLoaded={health.data?.models_loaded ?? true} onClose={() => setSelectedId(null)} onSimulate={simulate} />
      <PauseModal
        key={paying?.transaction.txn_id ?? "none"}
        item={paying}
        onDecline={() => {
          setPaying(null);
          notify("success", "Request declined. Nothing was paid. Report the payee in your UPI app.");
        }}
        onTrust={() => {
          setPaying(null);
          notify("info", "Simulated payment sent after two confirmations. In real life, this money would be gone.");
        }}
      />
      <Toast key={toast?.id} toast={toast} onDone={clearToast} />
    </>
  );
}
