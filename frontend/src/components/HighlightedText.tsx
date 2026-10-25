import type { Signal } from "@contracts/types";
import { useMemo } from "react";
import { SIGNAL_SLOTS } from "../lib/risk";
import { segmentText } from "../lib/spans";

interface Props {
  text: string;
  signals: Signal[];
  active: number | null;
  onActivate: (idx: number | null) => void;
}

/** The message re-rendered as plain text (never HTML) with evidence spans marked. */
export function HighlightedText({ text, signals, active, onActivate }: Props) {
  const segments = useMemo(() => segmentText(text, signals), [text, signals]);
  return (
    <p className="whitespace-pre-wrap break-words rounded-lg border border-line bg-surface-2 p-4 text-[15px] leading-[1.9] text-ink">
      {segments.map((seg, i) => {
        if (seg.signals.length === 0) return <span key={i}>{seg.text}</span>;
        // Colour by the strongest explainable rule; the model's wording signal only colours what no rule claimed.
        const idx = seg.signals.find((s) => signals[s].code !== "MODEL_TEXT") ?? seg.signals[0];
        const color = SIGNAL_SLOTS[idx % SIGNAL_SLOTS.length];
        const titles = seg.signals.map((s) => signals[s].title).join(" · ");
        const dim = active !== null && !seg.signals.includes(active);
        return (
          <mark
            key={i}
            tabIndex={0}
            title={titles}
            aria-label={`${seg.text} — ${titles}`}
            onMouseEnter={() => onActivate(idx)}
            onMouseLeave={() => onActivate(null)}
            onFocus={() => onActivate(idx)}
            onBlur={() => onActivate(null)}
            className="cursor-help rounded-[3px] px-0.5 text-ink transition-opacity"
            style={{
              backgroundColor: `${color}26`,
              boxShadow: `inset 0 -2px 0 ${color}`,
              opacity: dim ? 0.45 : 1,
            }}
          >
            {seg.text}
          </mark>
        );
      })}
    </p>
  );
}
