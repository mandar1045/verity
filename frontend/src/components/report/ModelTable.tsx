import type { ModelRow } from "@contracts/types";

type Row = ModelRow & { false_alarms_per_1000?: number };

interface Props {
  rows: Row[];
  highlight: string;
  caption: string;
  showFalseAlarms?: boolean;
}

const f3 = (x: number | null) => (x === null ? "—" : x.toFixed(3));

/** Baselines vs Verity. The Verity row carries the only accent colour; baselines stay grey. */
export function ModelTable({ rows, highlight, caption, showFalseAlarms = false }: Props) {
  return (
    <div className="overflow-x-auto rounded-lg border border-line">
      <table className="w-full min-w-[560px] text-sm">
        <caption className="sr-only">{caption}</caption>
        <thead className="bg-surface-2 text-xs text-ink-3">
          <tr>
            <th scope="col" className="px-4 py-2.5 text-left font-medium">Approach</th>
            <th scope="col" className="px-3 py-2.5 text-right font-medium">Precision</th>
            <th scope="col" className="px-3 py-2.5 text-right font-medium">Recall</th>
            <th scope="col" className="w-[32%] px-3 py-2.5 text-left font-medium">F1</th>
            <th scope="col" className="px-3 py-2.5 text-right font-medium">PR-AUC</th>
            {showFalseAlarms && <th scope="col" className="px-4 py-2.5 text-right font-medium">False alarms / 1,000</th>}
          </tr>
        </thead>
        <tbody className="num divide-y divide-line">
          {rows.map((r) => {
            const hi = r.key === highlight;
            return (
              <tr key={r.key} className={hi ? "bg-brand-50/70" : ""}>
                <th scope="row" className={`px-4 py-3 text-left font-medium ${hi ? "text-brand-800" : "text-ink-2"}`}>
                  {r.name}
                </th>
                <td className="px-3 py-3 text-right text-ink-2">{f3(r.precision)}</td>
                <td className="px-3 py-3 text-right text-ink-2">{f3(r.recall)}</td>
                <td className="px-3 py-3">
                  <div className="flex items-center gap-2.5">
                    <div className="h-2.5 flex-1 rounded-r bg-surface-3" aria-hidden>
                      <div className="h-2.5 rounded-r" style={{ width: `${r.f1 * 100}%`, background: hi ? "#1a4480" : "#a5abb6", borderRadius: "0 4px 4px 0" }} />
                    </div>
                    <span className={`w-11 text-right ${hi ? "font-semibold text-ink" : "text-ink-2"}`}>{f3(r.f1)}</span>
                  </div>
                </td>
                <td className="px-3 py-3 text-right text-ink-2">{f3(r.pr_auc)}</td>
                {showFalseAlarms && <td className="px-4 py-3 text-right text-ink-2">{r.false_alarms_per_1000?.toFixed(1)}</td>}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
