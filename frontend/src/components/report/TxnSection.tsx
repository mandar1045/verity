import type { TxnMetrics } from "@contracts/types";
import { BreakdownBars } from "./BreakdownBars";
import { ConfusionMatrix } from "./ConfusionMatrix";
import { ModelTable } from "./ModelTable";

const PATTERN: Record<string, string> = {
  collect_new_payee: "Collect from new payee",
  young_payee_large: "Large to brand-new payee",
  burst: "Burst of payments",
  night_high: "Night, far above usual",
  device_change_high: "New device, large amount",
  reported_payee: "Reported payee",
  just_under_limit: "Just under a limit",
  mule: "Money-mule outflow",
};

export function TxnSection({ t }: { t: TxnMetrics }) {
  const byKey = Object.fromEntries(t.models.map((r) => [r.key, r]));
  return (
    <section aria-labelledby="txn-eval" className="card card-pad space-y-8">
      <div>
        <p className="eyebrow">Transactions</p>
        <h2 id="txn-eval" className="mt-1 font-serif text-2xl font-semibold">
          Fraud detection on the last 15 days, trained only on the first 45
        </h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-ink-3">
          {t.test_size.toLocaleString("en-IN")} simulated payments from 200 users ({(t.fraud_rate_test * 100).toFixed(1)}% fraud). Chronological
          split, no shuffling across time. Rules act as a floor only when their score is at least {t.floor_min} (tuned on validation days
          39–45). Explanations: {t.explainer}.
        </p>
      </div>

      <ModelTable rows={t.models} highlight="gbm_floors" caption="Transaction models compared on days 46 to 60" showFalseAlarms />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <div className="grid gap-6 sm:grid-cols-2">
          {(["rules", "gbm_floors"] as const).map((k) =>
            byKey[k] ? <ConfusionMatrix key={k} title={byKey[k].name} matrix={byKey[k].confusion} positive="fraud" /> : null,
          )}
          <p className="text-[13px] leading-relaxed text-ink-3 sm:col-span-2">
            The unsupervised Isolation Forest is a reference point: without labels it flags oddities, not fraud. Every one of the{" "}
            <strong className="text-ink-2">{t.demo_frauds_flagged}</strong> frauds in the demo accounts is flagged.
          </p>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-ink">Recall by fraud pattern</h3>
          <p className="mb-3 text-xs text-ink-3">Verity (GBM + rule floors)</p>
          <BreakdownBars rows={t.recall_by_pattern} metric="Recall" nameOf={(g) => PATTERN[g] ?? g} />
        </div>
      </div>
    </section>
  );
}
