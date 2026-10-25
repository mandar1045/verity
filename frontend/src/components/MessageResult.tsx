import type { MessageAnalysis } from "@contracts/types";
import { useState } from "react";
import { useLang } from "../i18n/LangContext";
import { scamTypeName } from "../lib/format";
import { ExplanationPanel } from "./ExplanationPanel";
import { FeedbackButton } from "./FeedbackButton";
import { HighlightedText } from "./HighlightedText";
import { LinksTable } from "./LinksTable";
import { RiskGauge } from "./RiskGauge";
import { SignalList } from "./SignalList";
import { SectionTitle } from "./States";

function Meter({ label, value, hint }: { label: string; value: number; hint: string }) {
  return (
    <div>
      <div className="flex items-baseline justify-between text-xs">
        <span className="font-medium text-ink-2">{label}</span>
        <span className="num font-semibold text-ink">{value.toFixed(2)}</span>
      </div>
      <div className="mt-1 h-1.5 rounded-full bg-brand-50" aria-hidden>
        <div className="h-1.5 rounded-full bg-brand-500" style={{ width: `${Math.round(value * 100)}%` }} />
      </div>
      <p className="mt-1 text-[11px] text-ink-4">{hint}</p>
    </div>
  );
}

export function MessageResult({ result, text, stale }: { result: MessageAnalysis; text: string; stale: boolean }) {
  const { t, lang } = useLang();
  const [active, setActive] = useState<number | null>(null);
  const highlighted = result.signals.filter((s) => s.evidence.length > 0).length;
  const type = scamTypeName(result.scam_type, lang);

  return (
    <article className={`card transition-opacity ${stale ? "opacity-60" : ""}`} aria-live="polite" aria-busy={stale}>
      <div className="grid gap-6 border-b border-line p-5 sm:grid-cols-[auto_1fr] sm:p-6">
        <RiskGauge score={result.risk_score} label={result.label} />
        <div className="flex flex-col justify-center gap-4">
          {type ? (
            <div>
              <p className="eyebrow">{t("scamType")}</p>
              <p className="mt-0.5 font-serif text-xl font-semibold leading-snug">{type}</p>
            </div>
          ) : (
            <p className="font-serif text-xl font-semibold leading-snug">{result.label === "SAFE" ? "No scam pattern matched" : "Unusual message"}</p>
          )}
          <div className="grid gap-4 sm:grid-cols-2">
            <Meter label="ML model probability" value={result.model_prob} hint="TF-IDF + logistic regression" />
            <Meter label="Rule score" value={result.rule_score} hint={`${result.signals.length} signal${result.signals.length === 1 ? "" : "s"} fired`} />
          </div>
        </div>
      </div>

      <div className="space-y-6 p-5 sm:p-6">
        <ExplanationPanel label={result.label} explanation={result.explanation} steps={result.next_steps} source={result.explanation_source} />

        <section>
          <SectionTitle aside={highlighted ? "Hover or tab to a mark to see why" : undefined}>{t("yourMessage")}</SectionTitle>
          <HighlightedText text={text} signals={result.signals} active={active} onActivate={setActive} />
        </section>

        <section>
          <SectionTitle aside="Strongest first · weight 0–1">{t("signalsFound")}</SectionTitle>
          <SignalList signals={result.signals} active={active} onActivate={setActive} />
        </section>

        {result.links.length > 0 && (
          <section>
            <SectionTitle>{t("linksInMessage")}</SectionTitle>
            <LinksTable links={result.links} />
          </section>
        )}

        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
          <FeedbackButton key={result.id} analysisId={result.id} kind="message" current={result.label} />
          <p className="num text-[11px] text-ink-4">Analysis {result.id.slice(0, 8)}</p>
        </div>
      </div>
    </article>
  );
}
