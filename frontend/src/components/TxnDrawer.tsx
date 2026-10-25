import type { FeedItem } from "@contracts/types";
import { X } from "lucide-react";
import { inr, shortTime } from "../lib/format";
import { ContributionBars } from "./ContributionBars";
import { ExplanationPanel } from "./ExplanationPanel";
import { FeedbackButton } from "./FeedbackButton";
import { RiskGauge } from "./RiskGauge";
import { SignalList } from "./SignalList";
import { SectionTitle } from "./States";
import { useDialog } from "./useDialog";

interface Props {
  item: FeedItem | null;
  modelLoaded: boolean;
  onClose: () => void;
  onSimulate: (item: FeedItem) => void;
}

export function TxnDrawer({ item, modelLoaded, onClose, onSimulate }: Props) {
  const ref = useDialog<HTMLDivElement>(item !== null, onClose);
  if (!item) return null;
  const t = item.transaction;
  const a = item.analysis;
  const facts = [
    ["Payee UPI ID", t.payee_vpa],
    ["Paid via", t.channel],
    ["Payee account age", `${t.payee_account_age_days} days`],
    ["Reports against payee", String(t.payee_report_count)],
    ["New payee", t.payee_is_new ? "Yes" : "No"],
    ["New device", t.device_changed ? "Yes" : "No"],
  ];
  return (
    <div className="fixed inset-0 z-40" role="presentation">
      <div className="absolute inset-0 bg-ink/30" onClick={onClose} aria-hidden />
      <div
        ref={ref}
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        className="absolute inset-y-0 right-0 flex w-full max-w-xl flex-col bg-surface shadow-pop"
      >
        <header className="flex items-start justify-between gap-4 border-b border-line px-5 py-4 sm:px-6">
          <div>
            <p className="eyebrow">{t.type === "COLLECT_REQUEST" ? "Collect request" : t.type === "RECEIVE" ? "Money received" : "Payment"} · {shortTime(t.timestamp)}</p>
            <h2 id="drawer-title" className="mt-1 font-serif text-2xl font-semibold">
              {inr(t.amount_inr)} <span className="text-ink-3">{t.type === "RECEIVE" ? "from" : "to"}</span> {t.payee_name}
            </h2>
          </div>
          <button type="button" onClick={onClose} className="btn-ghost -mr-2 p-2" aria-label="Close details">
            <X className="h-5 w-5" aria-hidden />
          </button>
        </header>
        <div className="flex-1 space-y-6 overflow-y-auto px-5 py-5 sm:px-6">
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-center">
            <RiskGauge score={a.risk_score} label={a.label} size={170} />
            <dl className="grid flex-1 grid-cols-2 gap-x-4 gap-y-2 text-[13px]">
              {facts.map(([k, v]) => (
                <div key={k}>
                  <dt className="text-ink-4">{k}</dt>
                  <dd className="break-all font-medium text-ink">{v}</dd>
                </div>
              ))}
            </dl>
          </div>
          {t.type === "COLLECT_REQUEST" && (
            <button type="button" className="btn-primary w-full" onClick={() => onSimulate(item)}>
              Simulate paying this request
            </button>
          )}
          <ExplanationPanel label={a.label} explanation={a.explanation} steps={a.next_steps} source={a.explanation_source} stacked />
          <section>
            <SectionTitle aside="Top 5 by influence">Why the model scored it this way</SectionTitle>
            <ContributionBars items={a.feature_contributions} source={modelLoaded ? "shap" : "rules"} />
          </section>
          <section>
            <SectionTitle>Fraud patterns detected</SectionTitle>
            <SignalList signals={a.signals} />
          </section>
          <FeedbackButton key={t.txn_id} analysisId={t.txn_id} kind="transaction" current={a.label} />
        </div>
      </div>
    </div>
  );
}
