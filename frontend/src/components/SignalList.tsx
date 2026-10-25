import type { Signal } from "@contracts/types";
import { Sparkles } from "lucide-react";
import { useLang } from "../i18n/LangContext";
import { SIGNAL_SLOTS } from "../lib/risk";

interface Props {
  signals: Signal[];
  active?: number | null;
  onActivate?: (idx: number | null) => void;
}

const MODEL_CODES = new Set(["MODEL_TEXT", "MODEL_TXN"]);

/** Signal cards, strongest first. The swatch matches the highlight in the message. */
export function SignalList({ signals, active = null, onActivate }: Props) {
  const { t } = useLang();
  if (signals.length === 0) return <p className="text-sm text-ink-3">{t("noSignals")}</p>;
  return (
    <ul className="grid gap-2.5 sm:grid-cols-2">
      {signals.map((s, idx) => {
        const color = SIGNAL_SLOTS[idx % SIGNAL_SLOTS.length];
        const hasEvidence = s.evidence.length > 0;
        const isActive = active === idx;
        return (
          <li
            key={`${s.code}-${idx}`}
            onMouseEnter={() => onActivate?.(idx)}
            onMouseLeave={() => onActivate?.(null)}
            className={[
              "rounded-lg border bg-surface p-3.5 transition-colors",
              isActive ? "border-brand-300 bg-brand-50/40" : "border-line",
            ].join(" ")}
          >
            <div className="flex items-start gap-2.5">
              {hasEvidence ? (
                <span className="mt-1 h-3 w-3 shrink-0 rounded-[3px]" style={{ backgroundColor: color }} aria-hidden />
              ) : (
                <span className="mt-0.5 h-3 w-3 shrink-0" aria-hidden />
              )}
              <div className="min-w-0 flex-1">
                <div className="flex items-baseline justify-between gap-2">
                  <p className="flex items-center gap-1.5 text-sm font-semibold text-ink">
                    {MODEL_CODES.has(s.code) && <Sparkles className="h-3.5 w-3.5 text-brand-600" aria-label="from the ML model" />}
                    {s.title}
                  </p>
                  <span className="num shrink-0 text-xs font-medium text-ink-3" title="Signal weight">
                    {s.weight.toFixed(2)}
                  </span>
                </div>
                <p className="mt-0.5 break-words text-[13px] leading-relaxed text-ink-3">{s.description}</p>
                <div className="mt-2 h-1 rounded-full bg-surface-3" aria-hidden>
                  <div className="h-1 rounded-full bg-ink-3" style={{ width: `${Math.round(s.weight * 100)}%` }} />
                </div>
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
