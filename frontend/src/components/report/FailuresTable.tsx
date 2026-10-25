import type { FailureRow } from "@contracts/types";
import { humanize } from "../../lib/format";

const outcome = (r: FailureRow) => (r.true_label === 1 ? "Missed (false negative)" : "False alarm (false positive)");

/** The worst errors on held-out data, kept in on purpose. */
export function FailuresTable({ rows }: { rows: FailureRow[] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-line">
      <table className="w-full min-w-[720px] text-left text-sm">
        <caption className="sr-only">Worst errors on the held-out test data and why they failed</caption>
        <thead className="bg-surface-2 text-xs text-ink-3">
          <tr>
            <th scope="col" className="px-4 py-2.5 font-medium">Input</th>
            <th scope="col" className="px-3 py-2.5 font-medium">Outcome</th>
            <th scope="col" className="px-3 py-2.5 text-right font-medium">Score</th>
            <th scope="col" className="px-4 py-2.5 font-medium">Why it failed</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line align-top">
          {rows.map((r, i) => (
            <tr key={i}>
              <td className="max-w-[22rem] px-4 py-3">
                <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-ink-4">
                  {r.kind} · {humanize(r.group)}
                </p>
                <p className="break-words text-[13px] leading-relaxed text-ink">{r.text}</p>
              </td>
              <td className="whitespace-nowrap px-3 py-3 text-[13px] text-ink-2">{outcome(r)}</td>
              <td className="num px-3 py-3 text-right font-semibold text-ink">{r.score}</td>
              <td className="px-4 py-3 text-[13px] leading-relaxed text-ink-2">{r.why}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
