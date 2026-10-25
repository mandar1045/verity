import type { FeatureContribution } from "@contracts/types";

interface Props {
  items: FeatureContribution[];
  source: "shap" | "rules";
}

const UP = "#cc3a2e"; // pushes risk up
const DOWN = "#9aa1ad"; // pushes risk down (neutral grey)
const LABEL_ROOM = 44; // px reserved beyond the longest bar for its value label

/**
 * Horizontal bars from a shared baseline: centred when some reasons lower the risk,
 * left-aligned when all raise it. 12px thick, 4px rounded data end, value at the tip.
 */
export function ContributionBars({ items, source }: Props) {
  const max = Math.max(0.0001, ...items.map((i) => Math.abs(i.contribution)));
  const diverging = items.some((i) => i.contribution < 0);
  const span = diverging ? 0.5 : 1; // share of the track one side may use
  return (
    <figure>
      <ul className="space-y-3" aria-label="Reasons ranked by influence on the risk score">
        {items.map((it, i) => {
          const up = it.contribution >= 0;
          const frac = (Math.abs(it.contribution) / max) * span;
          const width = `calc(${frac} * (100% - ${diverging ? 2 * LABEL_ROOM : LABEL_ROOM}px))`;
          const origin = diverging ? "50%" : "0px";
          const value = `${up ? "+" : "−"}${Math.abs(it.contribution).toFixed(2)}`;
          const label = `${it.feature}: ${value} (${up ? "raises" : "lowers"} risk)`;
          return (
            <li key={i} title={label} aria-label={label}>
              <p className="mb-1 text-[13px] leading-snug text-ink-2">{it.feature}</p>
              <div className="relative h-3" aria-hidden>
                <div className="absolute inset-y-[-3px] w-px bg-line-strong" style={{ left: origin }} />
                <div
                  className="absolute top-0 h-3"
                  style={{
                    width,
                    ...(up ? { left: origin } : { right: `calc(100% - ${origin})` }),
                    background: up ? UP : DOWN,
                    borderRadius: up ? "0 4px 4px 0" : "4px 0 0 4px",
                  }}
                />
                <span
                  className="num absolute top-1/2 -translate-y-1/2 whitespace-nowrap text-[11px] font-semibold text-ink-2"
                  style={up ? { left: `calc(${origin} + ${width} + 6px)` } : { right: `calc(100% - ${origin} + ${width} + 6px)` }}
                >
                  {value}
                </span>
              </div>
            </li>
          );
        })}
      </ul>
      <figcaption className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-ink-3">
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-sm" style={{ background: UP }} /> Pushes risk up
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-sm" style={{ background: DOWN }} /> Pushes risk down
        </span>
        <span>{source === "shap" ? "SHAP values from the gradient-boosting model (log-odds)" : "Rule weights (model unavailable)"}</span>
      </figcaption>
    </figure>
  );
}
