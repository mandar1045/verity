import type { Label } from "@contracts/types";
import { useLang } from "../i18n/LangContext";
import { RISK } from "../lib/risk";

interface Props {
  label: Label;
  score?: number;
  size?: "sm" | "md";
}

/** Colour + icon + text, so risk never relies on colour alone. */
export function RiskBadge({ label, score, size = "sm" }: Props) {
  const { t } = useLang();
  const meta = RISK[label];
  const Icon = meta.icon;
  const pad = size === "md" ? "px-2.5 py-1 text-sm" : "px-2 py-0.5 text-xs";
  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border font-semibold ${pad} ${meta.bg} ${meta.border} ${meta.text}`}>
      <Icon className={size === "md" ? "h-4 w-4" : "h-3.5 w-3.5"} aria-hidden />
      {t(label)}
      {score !== undefined && <span className="num font-medium opacity-80">· {score}</span>}
    </span>
  );
}
