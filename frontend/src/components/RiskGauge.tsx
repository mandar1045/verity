import type { Label } from "@contracts/types";
import { useEffect, useState } from "react";
import { useLang } from "../i18n/LangContext";
import { RISK } from "../lib/risk";

interface Props {
  score: number;
  label: Label;
  size?: number;
}

const R = 80;
const ARC = Math.PI * R; // semicircle length

/**
 * Semicircle meter: the fill carries severity, the track is a lighter step of the
 * same ramp. The only animation in the app is this 200 ms reveal.
 */
export function RiskGauge({ score, label, size = 200 }: Props) {
  const { t } = useLang();
  const meta = RISK[label];
  const Icon = meta.icon;
  const [shown, setShown] = useState(0);

  useEffect(() => {
    setShown(0);
    const id = window.setTimeout(() => setShown(score), 30);
    return () => window.clearTimeout(id);
  }, [score]);

  const offset = ARC * (1 - Math.max(0, Math.min(100, shown)) / 100);
  return (
    <figure className="flex flex-col items-center" aria-label={`${t("riskScore")} ${score} of 100, ${t(label)}`} role="img">
      <svg viewBox="0 0 200 112" width={size} height={(size * 112) / 200} aria-hidden>
        <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke={meta.track} strokeWidth="16" strokeLinecap="round" />
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={meta.fill}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={ARC}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 200ms ease-out" }}
        />
        {[35, 70].map((tick) => {
          const a = Math.PI * (1 - tick / 100);
          return (
            <line
              key={tick}
              x1={100 + 66 * Math.cos(a)}
              y1={100 - 66 * Math.sin(a)}
              x2={100 + 58 * Math.cos(a)}
              y2={100 - 58 * Math.sin(a)}
              stroke="#c9c6bc"
              strokeWidth="2"
              strokeLinecap="round"
            />
          );
        })}
        <text x="100" y="92" textAnchor="middle" className="fill-ink" style={{ font: "600 40px Inter, system-ui, sans-serif" }}>
          {score}
        </text>
        <text x="100" y="108" textAnchor="middle" className="fill-ink-3" style={{ font: "500 10px Inter, system-ui, sans-serif" }}>
          / 100
        </text>
      </svg>
      <figcaption className={`mt-1 inline-flex items-center gap-1.5 text-base font-semibold ${meta.text}`}>
        <Icon className="h-5 w-5" aria-hidden />
        {t(label)}
      </figcaption>
    </figure>
  );
}
