import type { FeedItem, TxnType } from "@contracts/types";
import { ArrowDownLeft, ArrowUpRight, HandCoins } from "lucide-react";
import { inr, shortTime } from "../lib/format";
import { RiskBadge } from "./RiskBadge";

const TYPE: Record<TxnType, { label: string; icon: typeof ArrowUpRight; cls: string }> = {
  PAY: { label: "Pay", icon: ArrowUpRight, cls: "text-ink-2" },
  COLLECT_REQUEST: { label: "Collect request", icon: HandCoins, cls: "text-brand-700" },
  RECEIVE: { label: "Received", icon: ArrowDownLeft, cls: "text-safe-700" },
};

interface Props {
  items: FeedItem[];
  selected: string | null;
  onSelect: (item: FeedItem) => void;
  onSimulate: (item: FeedItem) => void;
}

export function TxnTable({ items, selected, onSelect, onSimulate }: Props) {
  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <caption className="sr-only">Recent transactions, newest first. Select a row to see why it was flagged.</caption>
          <thead className="border-b border-line bg-surface-2 text-xs text-ink-3">
            <tr>
              <th scope="col" className="px-4 py-2.5 font-medium">Time</th>
              <th scope="col" className="px-4 py-2.5 font-medium">Payee</th>
              <th scope="col" className="px-4 py-2.5 font-medium">Type</th>
              <th scope="col" className="px-4 py-2.5 text-right font-medium">Amount</th>
              <th scope="col" className="px-4 py-2.5 font-medium">Risk</th>
              <th scope="col" className="px-4 py-2.5"><span className="sr-only">Action</span></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {items.map((it) => {
              const t = it.transaction;
              const a = it.analysis;
              const flagged = a.label !== "SAFE";
              const type = TYPE[t.type];
              const Icon = type.icon;
              const isSel = selected === t.txn_id;
              const rowTone = a.label === "HIGH_RISK" ? "bg-danger-50/60" : a.label === "SUSPICIOUS" ? "bg-warn-50/60" : "";
              return (
                <tr
                  key={t.txn_id}
                  tabIndex={0}
                  aria-selected={isSel}
                  onClick={() => onSelect(it)}
                  onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), onSelect(it))}
                  className={`cursor-pointer transition-colors hover:bg-surface-3 ${rowTone} ${isSel ? "outline outline-2 -outline-offset-2 outline-brand-500" : ""}`}
                >
                  <td className={`num whitespace-nowrap px-4 py-3 text-ink-3 ${flagged ? "border-l-[3px] " + (a.label === "HIGH_RISK" ? "border-l-danger-600" : "border-l-warn-600") : "border-l-[3px] border-l-transparent"}`}>
                    {shortTime(t.timestamp)}
                  </td>
                  <td className="px-4 py-3">
                    <p className="font-medium text-ink">{t.payee_name}</p>
                    <p className="font-mono text-[11.5px] text-ink-4">{t.payee_vpa}</p>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3">
                    <span className={`inline-flex items-center gap-1 text-[13px] font-medium ${type.cls}`}>
                      <Icon className="h-3.5 w-3.5" aria-hidden />
                      {type.label}
                    </span>
                  </td>
                  <td className={`num whitespace-nowrap px-4 py-3 text-right font-semibold ${t.type === "RECEIVE" ? "text-safe-700" : "text-ink"}`}>
                    {t.type === "RECEIVE" ? "+" : ""}
                    {inr(t.amount_inr)}
                  </td>
                  <td className="px-4 py-3">
                    <RiskBadge label={a.label} score={a.risk_score} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    {t.type === "COLLECT_REQUEST" && (
                      <button
                        type="button"
                        className="btn-secondary px-2.5 py-1 text-xs"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSimulate(it);
                        }}
                      >
                        Simulate payment
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
