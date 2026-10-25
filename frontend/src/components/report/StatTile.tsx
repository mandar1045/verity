import type { ReactNode } from "react";

/** Stat tile: label · value (sans, proportional figures) · context line. */
export function StatTile({ label, value, context, accent = false }: { label: string; value: ReactNode; context: string; accent?: boolean }) {
  return (
    <div className={`rounded-xl border p-4 ${accent ? "border-brand-200 bg-brand-50" : "border-line bg-surface"}`}>
      <p className="text-[13px] font-medium text-ink-3">{label}</p>
      <p className={`mt-1 text-[28px] font-semibold leading-tight tracking-tight ${accent ? "text-brand-800" : "text-ink"}`}>{value}</p>
      <p className="mt-1 text-xs leading-snug text-ink-3">{context}</p>
    </div>
  );
}
