import type { MessageMetrics } from "@contracts/types";
import { scamTypeName } from "../../lib/format";
import { BreakdownBars } from "./BreakdownBars";
import { ConfusionMatrix } from "./ConfusionMatrix";
import { ModelTable } from "./ModelTable";

const LANG_NAME: Record<string, string> = { en: "English", hinglish: "Hinglish", hi: "Hindi (Devanagari)", ta: "Tamil" };

export function MessageSection({ m }: { m: MessageMetrics }) {
  const byKey = Object.fromEntries(m.models.map((r) => [r.key, r]));
  return (
    <section aria-labelledby="msg-eval" className="card card-pad space-y-8">
      <div>
        <p className="eyebrow">Messages</p>
        <h2 id="msg-eval" className="mt-1 font-serif text-2xl font-semibold">
          Scam detection on message patterns the model never saw
        </h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-ink-3">
          {m.test_size.toLocaleString("en-IN")} test messages from {m.n_templates_test} template families held out of training
          ({m.train_size.toLocaleString("en-IN")} training messages). Fusion weight w = {m.fusion_weight} and every threshold were tuned on the
          validation split only.
        </p>
      </div>

      <ModelTable rows={m.models} highlight="fused" caption="Message models compared on the test split" />

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {(["keyword", "rules", "model", "fused"] as const).map((k) =>
          byKey[k] ? <ConfusionMatrix key={k} title={byKey[k].name} matrix={byKey[k].confusion} /> : null,
        )}
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <div>
          <h3 className="text-sm font-semibold text-ink">Recall by scam type</h3>
          <p className="mb-3 text-xs text-ink-3">Share of each scam type that Verity flagged</p>
          <BreakdownBars rows={m.recall_by_scam_type} metric="Recall" nameOf={(g) => scamTypeName(g) ?? g} />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-ink">F1 by language</h3>
          <p className="mb-3 text-xs text-ink-3">Tamil and Hindi have the least training data, and we say so</p>
          <BreakdownBars rows={m.f1_by_language} metric="F1" nameOf={(g) => LANG_NAME[g] ?? g} />
          <dl className="mt-6 grid grid-cols-2 gap-4 border-t border-line pt-4 text-sm">
            <div>
              <dt className="text-xs text-ink-3">False alarms on genuine messages</dt>
              <dd className="num mt-0.5 text-lg font-semibold">{(m.hard_negative_fpr * 100).toFixed(1)}%</dd>
            </div>
            <div>
              <dt className="text-xs text-ink-3">Scam type identified correctly</dt>
              <dd className="num mt-0.5 text-lg font-semibold">{(m.scam_type_accuracy * 100).toFixed(1)}%</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="rounded-lg border border-line bg-surface-2 p-4 sm:p-5">
        <h3 className="text-sm font-semibold text-ink">External check: UCI SMS Spam Collection (public, out of domain)</h3>
        <div className="num mt-3 flex flex-wrap gap-x-8 gap-y-2 text-sm">
          <span>
            Precision <strong>{m.external_uci.precision.toFixed(3)}</strong>
          </span>
          <span>
            Recall <strong>{m.external_uci.recall.toFixed(3)}</strong>
          </span>
          <span>
            F1 <strong>{m.external_uci.f1.toFixed(3)}</strong>
          </span>
          <span className="text-ink-3">n = {m.external_uci.n.toLocaleString("en-IN")}</span>
        </div>
        <p className="mt-3 text-[13px] leading-relaxed text-ink-3">{m.external_uci.note}</p>
        <p className="mt-2 text-[13px] leading-relaxed text-ink-3">
          <strong className="text-ink-2">What this check taught us:</strong> our first dataset had no everyday chat, so the model
          read casual messages as scams (UCI precision 0.146). We added an everyday-chat class written from scratch, never
          copied from UCI, and precision rose to {m.external_uci.precision.toFixed(3)}. Generic spam is still not what Verity is built for.
        </p>
      </div>
    </section>
  );
}
