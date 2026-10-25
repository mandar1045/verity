import { Info } from "lucide-react";
import { useState } from "react";
import { api } from "../api/client";
import { FailuresTable } from "../components/report/FailuresTable";
import { MessageSection } from "../components/report/MessageSection";
import { StatTile } from "../components/report/StatTile";
import { TxnSection } from "../components/report/TxnSection";
import { ErrorState, PageHeader, SkeletonCard } from "../components/States";
import { useAsync } from "../hooks/useAsync";

export default function ModelReport() {
  const metrics = useAsync(() => api.metrics(), []);
  const [allFailures, setAllFailures] = useState(false);
  const m = metrics.data;
  const fused = m?.message.models.find((r) => r.key === "fused");
  const rules = m?.message.models.find((r) => r.key === "rules");
  const txn = m?.transaction?.models.find((r) => r.key === "gbm_floors");

  return (
    <>
      <PageHeader eyebrow="Model report" title="How well does Verity actually work?">
        Every number here is computed on held-out data by <code className="font-mono text-[13px]">ml/eval/evaluate.py</code> and compared
        with simple baselines. Failures are shown, not hidden.
      </PageHeader>
      {metrics.error && <ErrorState message={metrics.error} onRetry={metrics.reload} />}
      {!m && !metrics.error && <SkeletonCard lines={10} />}
      {m && fused && rules && (
        <div className="space-y-8">
          <div className="flex gap-3 rounded-xl border border-warn-300 bg-warn-50 p-4 text-sm leading-relaxed text-warn-800">
            <Info className="mt-0.5 h-5 w-5 shrink-0" aria-hidden />
            <p>
              <strong>Read these scores with care.</strong> All training and test data is synthetic, so scores are higher than they
              would be on real messages. We guard against memorisation by testing only on template families the model never saw,
              by splitting transactions by time, and by an external check on the public UCI dataset below.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            <StatTile accent label="Message F1" value={fused.f1.toFixed(3)} context={`vs ${rules.f1.toFixed(3)} for rules alone`} />
            <StatTile label="Scams caught" value={`${(fused.recall * 100).toFixed(1)}%`} context="Recall on unseen templates" />
            <StatTile label="Precision" value={`${(fused.precision * 100).toFixed(1)}%`} context="Flags that were real scams" />
            {txn && <StatTile accent label="Transaction F1" value={txn.f1.toFixed(3)} context="GBM + rule floors, days 46–60" />}
            {txn && <StatTile label="False alarms" value={txn.false_alarms_per_1000.toFixed(1)} context="per 1,000 payments" />}
            {m.transaction && <StatTile label="Demo frauds flagged" value={m.transaction.demo_frauds_flagged} context="across the 3 demo accounts" />}
          </div>

          <MessageSection m={m.message} />
          {m.transaction && <TxnSection t={m.transaction} />}

          <section aria-labelledby="failures" className="card card-pad space-y-4">
            <div>
              <p className="eyebrow">Honest failures</p>
              <h2 id="failures" className="mt-1 font-serif text-2xl font-semibold">
                Where Verity gets it wrong
              </h2>
              <p className="mt-2 text-sm text-ink-3">The worst errors on held-out data, with the reason each one failed.</p>
            </div>
            <FailuresTable
              rows={
                allFailures
                  ? m.failures
                  : [...m.failures.filter((f) => f.kind === "message").slice(0, 5), ...m.failures.filter((f) => f.kind === "transaction").slice(0, 3)]
              }
            />
            {m.failures.length > 8 && (
              <button type="button" className="btn-secondary" onClick={() => setAllFailures((v) => !v)} aria-expanded={allFailures}>
                {allFailures ? "Show fewer" : `Show all ${m.failures.length} failures`}
              </button>
            )}
          </section>

          <p className="num text-xs text-ink-4">
            Generated {new Date(m.generated_at).toLocaleString("en-IN")} · data hash {m.data_hash} · message threshold {m.message.threshold}
            {m.transaction ? ` · transaction threshold ${m.transaction.threshold}` : ""}
          </p>
        </div>
      )}
    </>
  );
}
