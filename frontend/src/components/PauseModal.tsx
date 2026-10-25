import type { FeedItem } from "@contracts/types";
import { AlertOctagon, ShieldX } from "lucide-react";
import { useState } from "react";
import { useLang } from "../i18n/LangContext";
import { inr } from "../lib/format";
import { useDialog } from "./useDialog";

interface Props {
  item: FeedItem | null;
  onDecline: () => void;
  onTrust: () => void;
}

/** Full-screen interruption at the moment of payment. Declining is the default action. */
export function PauseModal({ item, onDecline, onTrust }: Props) {
  const { t } = useLang();
  const [armed, setArmed] = useState(false);
  const ref = useDialog<HTMLDivElement>(item !== null, onDecline);
  if (!item) return null;
  const reasons = item.analysis.signals.filter((s) => s.code !== "MODEL_TXN").slice(0, 2);
  const fallback = item.analysis.feature_contributions.filter((c) => c.contribution > 0).slice(0, 2);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-danger-50 p-4 sm:bg-ink/40" role="presentation">
      <div
        ref={ref}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="pause-title"
        aria-describedby="pause-body"
        className="w-full max-w-lg overflow-hidden rounded-2xl border border-danger-100 bg-surface shadow-pop"
      >
        <div className="bg-danger-700 px-6 py-6 text-white">
          <AlertOctagon className="h-10 w-10" aria-hidden />
          <h2 id="pause-title" className="mt-3 font-serif text-3xl font-semibold leading-tight">
            {t("pauseTitle")}
          </h2>
          <p className="mt-1 text-white/90">
            {inr(item.transaction.amount_inr)} → {item.transaction.payee_name} · risk {item.analysis.risk_score}/100
          </p>
        </div>
        <div className="space-y-5 px-6 py-6">
          <p id="pause-body" className="text-[15px] leading-relaxed text-ink">
            {t("pauseBody")}
          </p>
          <div>
            <p className="eyebrow mb-2">{t("topReasons")}</p>
            <ul className="space-y-2">
              {(reasons.length ? reasons.map((r) => r.title) : fallback.map((f) => f.feature)).map((text, i) => (
                <li key={i} className="flex items-start gap-2.5 rounded-lg border border-danger-100 bg-danger-50 px-3 py-2.5 text-sm font-medium text-danger-800">
                  <ShieldX className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
                  {text}
                </li>
              ))}
            </ul>
          </div>
          <div className="flex flex-col gap-2 pt-1 sm:flex-row-reverse">
            <button type="button" className="btn-danger flex-1 py-3 text-[15px]" onClick={onDecline}>
              {t("decline")}
            </button>
            <button
              type="button"
              className={`btn flex-1 border py-3 ${armed ? "border-danger-300 bg-danger-50 text-danger-800" : "border-line-strong bg-surface text-ink-2 hover:bg-surface-3"}`}
              onClick={() => (armed ? onTrust() : setArmed(true))}
            >
              {armed ? t("confirmTrust") : t("trust")}
            </button>
          </div>
          <p className="text-center text-xs text-ink-4">Simulation only. No real money moves. Verity advises; you decide.</p>
        </div>
      </div>
    </div>
  );
}
