import type { FeedItem } from "@contracts/types";
import { ChevronRight } from "lucide-react";
import { inr, shortTime } from "../lib/format";
import { RiskBadge } from "./RiskBadge";

interface Props {
  items: FeedItem[];
  onSelect: (item: FeedItem) => void;
  onSimulate: (item: FeedItem) => void;
}

const TYPE_LABEL = { PAY: "Pay", COLLECT_REQUEST: "Collect request", RECEIVE: "Received" } as const;

/** Phone layout of the feed: one card per payment, risk always visible. */
export function TxnList({ items, onSelect, onSimulate }: Props) {
  return (
    <ul className="space-y-2" aria-label="Recent transactions, newest first">
      {items.map((it) => {
        const t = it.transaction;
        const a = it.analysis;
        const tone = a.label === "HIGH_RISK" ? "border-l-danger-600 bg-danger-50/60" : a.label === "SUSPICIOUS" ? "border-l-warn-600 bg-warn-50/60" : "border-l-transparent bg-surface";
        return (
          <li key={t.txn_id} className={`rounded-xl border border-l-[3px] border-line ${tone}`}>
            <button type="button" onClick={() => onSelect(it)} className="flex w-full items-center gap-3 px-4 py-3 text-left">
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium text-ink">{t.payee_name}</p>
                <p className="num text-xs text-ink-3">
                  {shortTime(t.timestamp)} · {TYPE_LABEL[t.type]}
                </p>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className={`num text-sm font-semibold ${t.type === "RECEIVE" ? "text-safe-700" : "text-ink"}`}>
                  {t.type === "RECEIVE" ? "+" : ""}
                  {inr(t.amount_inr)}
                </span>
                <RiskBadge label={a.label} score={a.risk_score} />
              </div>
              <ChevronRight className="h-4 w-4 shrink-0 text-ink-4" aria-hidden />
            </button>
            {t.type === "COLLECT_REQUEST" && (
              <div className="border-t border-line px-4 py-2">
                <button type="button" className="btn-secondary w-full py-1.5 text-xs" onClick={() => onSimulate(it)}>
                  Simulate payment
                </button>
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
