import type { LinkFinding, LinkVerdict } from "@contracts/types";
import { AlertOctagon, AlertTriangle, CheckCircle2, type LucideIcon } from "lucide-react";
import { useLang } from "../i18n/LangContext";

const VERDICT: Record<LinkVerdict, { icon: LucideIcon; cls: string; text: string }> = {
  OK: { icon: CheckCircle2, cls: "bg-safe-50 text-safe-700 border-safe-300", text: "OK" },
  SUSPICIOUS: { icon: AlertTriangle, cls: "bg-warn-50 text-warn-700 border-warn-300", text: "Suspicious" },
  DANGEROUS: { icon: AlertOctagon, cls: "bg-danger-50 text-danger-700 border-danger-300", text: "Dangerous" },
};

/** Links are rendered as inert text. Verity never fetches or opens them. */
export function LinksTable({ links }: { links: LinkFinding[] }) {
  const { t } = useLang();
  if (links.length === 0) return null;
  return (
    <div>
      <div className="overflow-hidden rounded-lg border border-line">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface-2 text-xs text-ink-3">
            <tr>
              <th scope="col" className="px-3 py-2 font-medium">Link (as written)</th>
              <th scope="col" className="hidden px-3 py-2 font-medium sm:table-cell">Real domain</th>
              <th scope="col" className="px-3 py-2 font-medium">Verdict</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {links.map((lk, i) => {
              const v = VERDICT[lk.verdict];
              const Icon = v.icon;
              return (
                <tr key={i} className="align-top">
                  <td className="max-w-[16rem] px-3 py-3">
                    <code className="break-all font-mono text-[12.5px] text-ink">{lk.raw}</code>
                    <ul className="mt-1.5 space-y-0.5 text-[12.5px] leading-snug text-ink-3">
                      {lk.reasons.map((r, j) => (
                        <li key={j}>{r}</li>
                      ))}
                    </ul>
                  </td>
                  <td className="hidden px-3 py-3 sm:table-cell">
                    <code className="break-all font-mono text-[12.5px] text-ink-2">{lk.domain}</code>
                    {lk.lookalike_of && <p className="mt-1 text-xs text-ink-3">imitates {lk.lookalike_of}</p>}
                  </td>
                  <td className="px-3 py-3">
                    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-semibold ${v.cls}`}>
                      <Icon className="h-3.5 w-3.5" aria-hidden />
                      {v.text}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-ink-3">{t("linksNote")}</p>
    </div>
  );
}
