import type { ExplanationSource, Label } from "@contracts/types";
import { useLang } from "../i18n/LangContext";
import { RISK } from "../lib/risk";

interface Props {
  label: Label;
  explanation: string;
  steps: string[];
  source: ExplanationSource;
  stacked?: boolean;
}

export function ExplanationPanel({ label, explanation, steps, source, stacked = false }: Props) {
  const { t } = useLang();
  const meta = RISK[label];
  return (
    <div className={`grid gap-4 ${stacked ? "" : "lg:grid-cols-2"}`}>
      <section className={`rounded-lg border p-4 ${meta.bg} ${meta.border}`} aria-labelledby="why-title">
        <h3 id="why-title" className={`text-sm font-semibold ${meta.text}`}>
          {t("why")}
        </h3>
        <p className="mt-1.5 text-[15px] leading-relaxed text-ink">{explanation}</p>
        <p className="mt-3 text-[11px] font-medium uppercase tracking-wider text-ink-3">
          {source === "llm" ? "Re-phrased by an LLM from the template; verdict unchanged" : "Deterministic template · no LLM involved"}
        </p>
      </section>
      <section className="rounded-lg border border-line bg-surface p-4" aria-labelledby="todo-title">
        <h3 id="todo-title" className="text-sm font-semibold text-ink">
          {t("whatToDo")}
        </h3>
        <ol className="mt-2 space-y-2">
          {steps.map((s, i) => (
            <li key={i} className="flex gap-2.5 text-[14px] leading-relaxed text-ink-2">
              <span className="num mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-50 text-[11px] font-semibold text-brand-800">
                {i + 1}
              </span>
              <span>{s}</span>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
